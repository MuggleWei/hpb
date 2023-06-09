import getopt
import logging
import os
import shutil
import sys
from hpb.component.db_handle import DBHandle

from hpb.component.settings_handle import SettingsHandle
from hpb.component.yaml_handle import YamlHandle
from hpb.data_type.constant_var import APP_NAME
from hpb.data_type.package_info import PackageInfo
from hpb.data_type.package_meta import PackageMeta
from hpb.mapper.mapper_pkg import MapperPkg
from hpb.utils.utils import Utils


class UploaderConfig:
    def __init__(self):
        self.pkg_dir = ""
        self.pkg_file = ""


class Uploader:
    """
    package uplader
    """

    def __init__(self):
        """
        init package uploader
        """
        self._usage_str = "Usage: {0} push [OPTIONS]\n" \
            "\n" \
            "Options: \n" \
            "  -d, --pkg-dir string    [OPTIONAL] package directory, by default, search ./pkg.yml to find package directory\n" \
            "  -p, --pkg-file string   [OPTIONAL] package file, by default, search ./pkg.yml to find package directory\n" \
            "\n" \
            "e.g.\n" \
            "  {0} push" \
            "  {0} push -p ./pkg.yml" \
            "  {0} push -d pkg" \
            "\n" \
            "NOTE: \n" \
            "  When specify -d and -p in the same time, will ignore -p\n" \
            "".format(APP_NAME)

    def run(self, args):
        """
        run package uploader
        """
        if self._init(args=args) is False:
            return False

        if self._check_pkg_dir() is False:
            return False

        self.meta_file = os.path.join(self.pkg_dir, "{}.yml".format(APP_NAME))
        self.pkg_meta = PackageMeta()
        if self.pkg_meta.load_from_file(filepath=self.meta_file) is False:
            return False

        for output_repo in SettingsHandle().pkg_upload_repos:
            if output_repo.kind == "local":
                dirpath = self.pkg_meta.gen_pkg_dirpath()
                dirpath = os.path.join(
                    output_repo.path,
                    dirpath
                )
                if os.path.exists(dirpath):
                    shutil.rmtree(dirpath)

                logging.info(
                    "push {} -> {}".format(self.pkg_dir, dirpath))
                shutil.copytree(self.pkg_dir, dirpath)

                pkg_info = PackageInfo()
                pkg_info.path = dirpath
                pkg_info.meta = self.pkg_meta
                db_path = SettingsHandle().db_path
                with DBHandle(db_path, isolation_level="EXCLUSIVE") as \
                        db_handle:
                    mapper_pkg = MapperPkg()
                    mapper_pkg.insert(db_handle.conn, [pkg_info])
            else:
                logging.warning(
                    "Artifacts push to remote repo currently not support")

        return True

    def _check_pkg_dir(self):
        """
        check package directory is valid
        """
        art_files = os.listdir(self.pkg_dir)
        pkg_files = []
        meta_files = []
        for art_file in art_files:
            if art_file.endswith(".tar.gz"):
                pkg_files.append(art_file)
            elif art_file.endswith(".yml"):
                meta_files.append(art_file)

        if len(pkg_files) == 0:
            logging.error("Can't find package file in {}\n".format(self.pkg_dir))
            return False
        if len(pkg_files) > 1:
            logging.error("Multiple package file in {}\n{}\n".format(
                self.pkg_dir,
                "\n".join(pkg_files)
            ))
            return False

        if len(meta_files) == 0:
            logging.error("Can't find meta file in {}\n".format(self.pkg_dir))
            return False
        if len(meta_files) > 1:
            logging.error("Multiple meta file in {}\n{}\n".format(
                self.pkg_dir,
                "\n".join(meta_files)
            ))
            return False

        return True

    def _init(self, args):
        """
        init input arguments
        """
        self.cfg = self._parse_args(args=args)
        if self.cfg is None:
            return False

        self.pkg_dir = ""
        self.pkg_file = Utils.expand_path("./pkg.yml")
        if len(self.cfg.pkg_dir) != 0:
            self.pkg_dir = self.cfg.pkg_dir
        if len(self.cfg.pkg_file) != 0:
            self.pkg_file = self.cfg.pkg_file

        if len(self.pkg_dir) == 0:
            self.pkg_dir = self._get_pkg_dir_from_yml(self.pkg_file)
        if len(self.pkg_dir) == 0:
            return False

        if len(SettingsHandle().pkg_upload_repos) == 0:
            logging.error("'packages/upload' not be set in settings file")
            return False

        return True

    def _get_pkg_dir_from_yml(self, filepath):
        """
        get pkg dir from yml file
        """
        yaml_handle = YamlHandle()
        pkg_info = yaml_handle.load(filepath)
        if pkg_info is None:
            logging.error(
                "failed load package config file: {}".format(filepath))
            return ""
        return pkg_info["pkg_dir"]

    def _parse_args(self, args):
        """
        parse arguments
        """
        cfg = UploaderConfig()
        opts, _ = getopt.getopt(
            args, "hd:p:",
            [
                "help", "pkg-dir=", "pkg-file="
            ]
        )

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(self._usage_str)
                sys.exit(0)
            elif opt in ("-d", "--pkg-dir"):
                cfg.pkg_dir = arg
            elif opt in ("-p", "--pkg-file"):
                cfg.pkg_file = arg

        cfg.pkg_dir = Utils.expand_path(cfg.pkg_dir)
        cfg.pkg_file = Utils.expand_path(cfg.pkg_file)

        return cfg
