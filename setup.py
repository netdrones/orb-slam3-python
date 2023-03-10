import os
import sys
import subprocess
import shutil
from pathlib import Path
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

__version__ = '1.0.0'


class CMakeExtension(Extension):
    def __init__(self, name: str, src_dir: str = "") -> None:
        super().__init__(name, sources=[])
        self.source_dir = os.fspath(Path(src_dir).resolve())


class CMakeBuild(build_ext):
    def build_extension(self, ext) -> None:
        ext_fullpath = Path.cwd() / self.get_ext_fullpath(ext.name)
        extdir = ext_fullpath.parent.resolve()

        debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug

        cfg = "Debug" if debug else "Release"

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}{os.sep}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={cfg}",
        ]

        build_args = []

        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            # self.parallel is a Python 3 only way to set parallel jobs by hand
            # using -j in the build_ext call, not supported by pip or PyPA-build.
            if hasattr(self, "parallel") and self.parallel:
                # CMake 3.12+ only.
                build_args += [f"-j{self.parallel}"]

        if "CMAKE_ARGS" in os.environ:
            cmake_args += [x for x in os.environ["CMAKE_ARGS"].split(" ") if x]

        build_temp = Path(self.build_temp) / ext.name
        if not build_temp.exists():
          build_temp.mkdir(parents=True)

        # Build ORB-SLAM3 and dependencies
        print(os.path.join(Path.cwd(), "vendor", "ORB_SLAM3"))
        subprocess.run(
            ["/bin/sh", "build_libs.sh"], cwd=os.path.join(Path.cwd(), "vendor", "ORB_SLAM3")
        )
        # FIXME(rakuto): Workaround for broken linker...
        shutil.copyfile(Path.cwd() / "vendor" / "ORB_SLAM3" / "lib" / "libORB_SLAM3.so", "/usr/local/lib/libORB_SLAM3.so")

        subprocess.run(
            ["cmake", ext.source_dir, *cmake_args], cwd=build_temp, check=True
        )
        subprocess.run(
            ["cmake", "--build", ".", *build_args], cwd=build_temp, check=True
        )


setup(
    name="orb_slam3",
    version=__version__,
    author="Rakuto Furutani",
    author_email="rakuto@gmail.com",
    description="Python binding for ORB-SLAM3",
    ext_modules=[CMakeExtension("orb_slam3")],
    cmdclass={"build_ext": CMakeBuild},
    zip_safe=False,
    extras_require={"test": ["pytest>=6.0"]},
    python_requires=">=3.8",
    packages=["orb_slam3"],
)
