import getopt
import os
import shutil
import sys
import tarfile

from hpb.constant_var import APP_NAME
from hpb.utils import Utils


class DownloaderConfig:
    def __init__(self):
        self.repo_type = ""
        self.path = ""
        self.dest = ""
        self.extract = False


class Downloader:
    """
    package downloader
    """

    def __init__(self):
        """
        init package downloader
        """
        self._usage_str = "Usage: {0} pull [OPTIONS]\n" \
            "\n" \
            "Options: \n" \
            "  -t, --type string    [REQUIRED] local or remote\n" \
            "  -p, --path string    [REQUIRED] package path or url\n" \
            "  -d, --dest string    [REQUIRED] download destination\n" \
            "  -x, --extract string [OPTIONAL] extract files from packags\n" \
            "e.g.\n" \
            "  {0} pull -t local -p ~/.hpb/artifacts/google/googletest/v1.13.0-release-linux-arch-x86_64/googletest-v1.13.0-release-linux-x86_64.tar.gz\n" \
            "".format(APP_NAME)

    def run(self, args):
        """
        run package downloader
        """
        cfg = self._init(args=args)
        if cfg is None:
            return False
        return self.download(cfg=cfg)

    def _init(self, args):
        """
        init input arguments
        """
        cfg = self._parse_args(args=args)

        if len(cfg.repo_type) == 0:
            print("pull package without field 'type'\n\n"
                  "{}".format(self._usage_str))
            return None
        if len(cfg.path) == 0:
            print("pull package without field 'path'\n\n"
                  "{}".format(self._usage_str))
            return None
        if len(cfg.dest) == 0:
            print("pull package without field 'dest'\n\n"
                  "{}".format(self._usage_str))
            return None

        return cfg

    def download(self, cfg):
        """
        download package
        """
        self.cfg: DownloaderConfig = cfg
        if self.cfg.repo_type == "local":
            ret = self._download_local()
        else:
            print("unregconize repot_type: {}".format(self.cfg.repo_type))
            ret = False

        if ret is False:
            return ret

        if self.cfg.extract is True:
            self._extract(self.cfg)

        return True

    def _extract(self, cfg):
        """
        extract artifacts
        """
        dest = Utils.expand_path(cfg.dest)
        if dest.endswith("tar.gz"):
            dest = os.path.dirname(dest)

        filename = os.path.basename(cfg.path)

        origin_dir = os.path.abspath(os.curdir)
        os.chdir(dest)

        with tarfile.open(filename) as f:
            f.extractall(".")
        os.remove(filename)

        os.chdir(origin_dir)

    def _download_local(self):
        """
        download local artifacts
        """
        self.cfg.path = Utils.expand_path(self.cfg.path)
        dest = Utils.expand_path(self.cfg.dest)
        if dest.endswith("tar.gz"):
            dest = os.path.dirname(dest)

        if not os.path.isdir(dest):
            os.makedirs(dest, exist_ok=True)
        shutil.copy(self.cfg.path, dest)

        return True

    def _parse_args(self, args):
        """
        parse arguments
        """
        cfg = DownloaderConfig()
        try:
            opts, _ = getopt.getopt(
                args, "ht:p:d:x",
                [
                    "help", "type=", "path=", "dest=", "extract"
                ]
            )
        except Exception as e:
            print("{}, exit...".format(str(e)))
            sys.exit(1)

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(self._usage_str)
                sys.exit(0)
            elif opt in ("-t", "--type"):
                cfg.repo_type = arg
            elif opt in ("-p", "--path"):
                cfg.path = arg
            elif opt in ("-d", "--dest"):
                cfg.dest = arg
            elif opt in ("-x", "--extract"):
                cfg.extract = True

        return cfg