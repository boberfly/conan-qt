
import os
from conans import ConanFile, tools #, ConfigureEnvironment
from conans.tools import cpu_count, vcvars_command, os_info, SystemPackageTool
from distutils.spawn import find_executable

def which(program):
    """
    Locate a command.
    """
    def is_exe(fpath):
        """
        Check if a path is executable.
        """
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

class QtConan(ConanFile):
    """ Qt Conan package """

    name = "Qt"
    version = "5.6.1-adsk"
    description = "Conan.io package for Qt library."
    sourceDir = "qt-adsk-5.6.1"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "opengl": ["desktop", "dynamic"],
        "websockets": [True, False],
        "xmlpatterns": [True, False]
    }
    default_options = "shared=True", "opengl=desktop", "websockets=False", "xmlpatterns=False"
    url = "http://github.com/boberfly/conan-qt"
    license = "http://doc.qt.io/qt-5/lgpl.html"
    short_paths = True
    requires = "OpenSSL/1.0.2n@conan/stable"

    def system_requirements(self):
        pack_names = None
        if os_info.linux_distro == "ubuntu":
            pack_names = ["libgl1-mesa-dev", "libxcb1", "libxcb1-dev",
                          "libx11-xcb1", "libx11-xcb-dev", "libxcb-keysyms1",
                          "libxcb-keysyms1-dev", "libxcb-image0", "libxcb-image0-dev",
                          "libxcb-shm0", "libxcb-shm0-dev", "libxcb-icccm4",
                          "libxcb-icccm4-dev", "libxcb-sync1", "libxcb-sync-dev",
                          "libxcb-xfixes0-dev", "libxrender-dev", "libxcb-shape0-dev",
                          "libxcb-randr0-dev", "libxcb-render-util0", "libxcb-render-util0-dev",
                          "libxcb-glx0-dev", "libxcb-xinerama0", "libxcb-xinerama0-dev"]

            if self.settings.arch == "x86":
                full_pack_names = []
                for pack_name in pack_names:
                    full_pack_names += [pack_name + ":i386"]
                pack_names = full_pack_names

        if pack_names:
            installer = SystemPackageTool()
            installer.update() # Update the package database
            installer.install(" ".join(pack_names)) # Install the package

    def source(self):
        tools.get("https://www.autodesk.com/content/dam/autodesk/www/Company/files/Qt561ForMaya2018Update1.zip")
        tools.untargz("5.6.1-Maya/qt-adsk-5.6.1.tgz")

    def build(self):
        """ Define your project building. You decide the way of building it
            to reuse it later in any other project.
        """
        openssl_dir = self.deps_cpp_info["OpenSSL"].rootpath
        openssl_include = "%s/include" % openssl_dir
        openssl_lib = "%s/lib" % openssl_dir

        args = ["-prefix %s" % self.package_folder,
                "-plugindir %s/qt/plugins" % self.package_folder,
                "-opensource",
                "-confirm-license",
                "-no-rpath",
                "-no-gtkstyle",
                "-no-audio-backend",
                "-no-dbus",
                "-skip qtconnectivity",
                "-skip qtwebengine",
                "-skip qt3d",
                "-skip qtdeclarative",
                "-no-libudev",
                "-no-icu",
                "-qt-pcre",
                "-nomake examples",
                "-nomake tests",
                "-opengl desktop",
                #"-openssl",
                "-I %s" % openssl_include,
                "-L %s" % openssl_lib,
                "-no-warnings-are-errors"]
        if not self.options.shared:
            args.insert(0, "-static")
        if self.settings.build_type == "Debug":
            args.append("-debug")
        else:
            args.append("-release")

        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio":
                self._build_msvc(args)
            else:
                self._build_mingw(args)
        else:
            self._build_unix(args)

    def _build_msvc(self, args):
        build_command = find_executable("jom.exe")
        if build_command:
            build_args = ["-j", str(cpu_count())]
        else:
            build_command = "nmake.exe"
            build_args = []
        self.output.info("Using '%s %s' to build" % (build_command, " ".join(build_args)))

        vcvars = vcvars_command(self.settings)
        vcvars = vcvars + " && " if vcvars else ""
        set_env = 'SET PATH={dir}/qtbase/bin;{dir}/gnuwin32/bin;%PATH%'.format(dir=self.conanfile_directory)
        args += ["-no-angle"]
        # it seems not enough to set the vcvars for older versions, it works fine
        # with MSVC2015 without -platform
        if self.settings.compiler == "Visual Studio":
            if self.settings.compiler.version == "12":
                args += ["-platform win32-msvc2013"]
            if self.settings.compiler.version == "11":
                args += ["-platform win32-msvc2012"]
            if self.settings.compiler.version == "10":
                args += ["-platform win32-msvc2010"]

        self.run("cd %s && %s && %s configure %s"
                 % (self.sourceDir, set_env, vcvars, " ".join(args)))
        self.run("cd %s && %s %s %s"
                 % (self.sourceDir, vcvars, build_command, " ".join(build_args)))
        self.run("cd %s && %s %s install" % (self.sourceDir, vcvars, build_command))

    def _build_mingw(self, args):
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        args += ["-developer-build", "-opengl %s" % self.options.opengl, "-platform win32-g++"]

        self.output.info("Using '%s' threads" % str(cpu_count()))
        self.run("%s && cd %s && configure.bat %s"
                 % (env.command_line_env, self.sourceDir, " ".join(args)))
        self.run("%s && cd %s && mingw32-make -j %s"
                 % (env.command_line_env, self.sourceDir, str(cpu_count())))
        self.run("%s && cd %s && mingw32-make install" % (env.command_line_env, self.sourceDir))

    def _build_unix(self, args):
        if self.settings.os == "Linux":
            args += ["-qt-xcb"]
            if self.settings.arch == "x86":
                args += ["-platform linux-g++-32"]
        else:
            args += ["-silent", "-no-framework", "-no-freetype"]
            if self.settings.arch == "x86":
                args += ["-platform macx-clang-32"]

        self.output.info("Using '%s' threads" % str(cpu_count()))
        self.run("cd %s/%s && ./configure %s" % (self.source_folder, self.sourceDir, " ".join(args)))
        self.run("cd %s/%s && make -j %s" % (self.source_folder, self.sourceDir, str(cpu_count())))
        self.run("cd %s/%s && make install" % (self.source_folder, self.sourceDir))

    def package_info(self):
        libs = ['Concurrent', 'Core',
                'Gui', 'Network', 'OpenGL',
                'Widgets', 'Xml']

        self.cpp_info.libs = []
        self.cpp_info.includedirs = ["include"]
        for lib in libs:
            if self.settings.os == "Windows" and self.settings.build_type == "Debug":
                suffix = "d"
            elif self.settings.os == "Macos" and self.settings.build_type == "Debug":
                suffix = "_debug"
            else:
                suffix = ""
            self.cpp_info.libs += ["Qt5%s%s" % (lib, suffix)]
            self.cpp_info.includedirs += ["include/Qt%s" % lib]

        if self.settings.os == "Windows":
            # Some missing shared libs inside QML and others, but for the test it works
            self.env_info.path.append(os.path.join(self.package_folder, "bin"))
