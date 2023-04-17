import json
import unittest

from hpb.package_meta import PackageMeta
from hpb.yaml_handle import YamlHandle


class TestPackageMeta(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self._obj = {
            "name": "hpb",
            "maintainer": "mugglewei",
            "tag": "1.0.0",
            "build_type": "release",
            "is_fat_pkg": False,
            "platform": {
                "system": "linux",
                "release": "6.2.9-arch1-1",
                "version": "#1 SMP PREEMPT_DYNAMIC Thu, 30 Mar 2023 14:51:14 +0000",
                "machine": "x86_64",
                "distr_id": "arch",
                "distr_ver": "",
                "libc_id": "glibc",
                "libc_ver": "2.37"
            },
            "deps": []
        }

    def test_load(self):
        pkg_meta = PackageMeta()
        pkg_meta.load(obj=self._obj)
        self.assert_pkg_meta_eq(pkg_meta)

    def test_get_dict(self):
        pkg_meta = PackageMeta()
        pkg_meta.load(obj=self._obj)
        ordered_dict = pkg_meta.get_ordered_dict()
        self.assertDictEqual(ordered_dict, self._obj)

    def test_get_str(self):
        pkg_meta = PackageMeta()
        pkg_meta.load(obj=self._obj)
        s = str(pkg_meta)
        pkg_meta_obj = json.loads(s)
        self.assertDictEqual(pkg_meta_obj, self._obj)

    def test_load_from_file(self):
        pkg_meta = PackageMeta()
        ret = pkg_meta.load_from_file("./pkg/test_package_meta/hpb.yml")
        self.assertTrue(ret)
        self.assert_pkg_meta_eq(pkg_meta)

    def test_dump_to_file(self):
        pkg_meta = PackageMeta()
        pkg_meta.load_from_file("./pkg/test_package_meta/hpb.yml")

        output_filepath = "./_hpb/test_package_meta/hpb.yml"
        pkg_meta.dump(output_filepath)
        handle = YamlHandle()
        obj = handle.load(output_filepath)
        self.assertIsNotNone(obj)
        self.assert_dict_eq(obj, self._obj)

    def assert_pkg_meta_eq(self, pkg_meta: PackageMeta):
        src_info = pkg_meta.source_info
        self.assertEqual(src_info.name, self._obj["name"])
        self.assertEqual(src_info.maintainer, self._obj["maintainer"])
        self.assertEqual(src_info.tag, self._obj["tag"])

        self.assertEqual(pkg_meta.build_type, self._obj["build_type"])
        self.assertEqual(pkg_meta.is_fat_pkg, self._obj["is_fat_pkg"])

        meta_platform = pkg_meta.platform
        obj_platform = self._obj["platform"]
        self.assertEqual(meta_platform.system, obj_platform["system"])
        self.assertEqual(meta_platform.release, obj_platform["release"])
        self.assertEqual(meta_platform.version, obj_platform["version"])
        self.assertEqual(meta_platform.machine, obj_platform["machine"])
        self.assertEqual(meta_platform.distr_id, obj_platform["distr_id"])
        self.assertEqual(meta_platform.distr_ver, obj_platform["distr_ver"])
        self.assertEqual(meta_platform.libc_id, obj_platform["libc_id"])
        self.assertEqual(meta_platform.libc_ver, obj_platform["libc_ver"])

    def assert_dict_eq(self, obj1, obj2):
        for k, v in obj1.items():
            obj_v = obj2.get(k, None)
            self.assertIsNotNone(obj_v)
            if obj_v is None:
                continue
            if type(v) is dict:
                self.assert_dict_eq(v, obj_v)
            elif type(v) is list:
                # TODO: add object in deps
                pass
            else:
                self.assertEqual(v, obj_v)


if __name__ == "__main__":
    unittest.main()