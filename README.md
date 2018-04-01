Conan package for Qt
--------------------------------------------

[Conan.io](https://conan.io) package for [Qt](https://www.qt.io) library. This package includes by default the Qt Base module (Core, Gui, Widgets, Network, ...). Others modules can be added using options.

The packages generated with this **conanfile** can be found in [conan.io](http://www.conan.io/source/Qt/5.6.1-adsk/boberfly/stable).

## Reuse the package

### Basic setup

```
$ conan install Qt/5.6.1-adsk@boberfly/stable
```

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
```
    [requires]
    Qt/5.6.1-adsk@boberfly/stable

    [options]
    Qt:shared=true # false
    # On Windows, you can choose the opengl mode, default is 'desktop'
    Qt:opengl=desktop # dynamic
    # If you need specific Qt modules, you can add them as follow:
    Qt:websockets=true
    Qt:xmlpatterns=true

    [generators]
    txt
    cmake
```
Complete the installation of requirements for your project running:
```
    conan install .
```
Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.

## Develop the package

### Build packages

    $ pip install conan_package_tools
    $ python build.py

### Upload packages to server

    $ conan upload Qt/5.6.1-adsk@boberfly/stable --all
