#!/usr/bin/env python
# encoding: utf-8
import sys
import glob
sys.path.insert(0, sys.path[0]+'/waf_tools')

VERSION = '1.0.0'
APPNAME = 'robot_dart'

srcdir = '.'
blddir = 'build'

from waflib.Build import BuildContext
import dart
import boost
import eigen
import hexapod_controller


def options(opt):
    opt.load('compiler_cxx')
    opt.load('compiler_c')
    opt.load('boost')
    opt.load('eigen')
    opt.load('dart')
    opt.load('hexapod_controller')

    opt.add_option('--shared', action='store_true', help='build shared library', dest='build_shared')


def configure(conf):
    conf.get_env()['BUILD_GRAPHIC'] = False

    conf.load('compiler_cxx')
    conf.load('compiler_c')
    conf.load('boost')
    conf.load('eigen')
    conf.load('dart')
    conf.load('hexapod_controller')

    conf.check_boost(lib='regex system filesystem', min_version='1.46')
    conf.check_eigen()
    conf.check_dart()
    conf.check_hexapod_controller()

    conf.env['lib_type'] = 'cxxstlib'
    if conf.options.build_shared:
        conf.env['lib_type'] = 'cxxshlib'

    if conf.env.CXX_NAME in ["icc", "icpc"]:
        common_flags = "-Wall -std=c++11"
        opt_flags = " -O3 -xHost -mtune=native -unroll -g"
    elif conf.env.CXX_NAME in ["clang"]:
        common_flags = "-Wall -std=c++11"
        opt_flags = " -O3 -march=native -g"
    else:
        if int(conf.env['CC_VERSION'][0]+conf.env['CC_VERSION'][1]) < 47:
            common_flags = "-Wall -std=c++0x"
        else:
            common_flags = "-Wall -std=c++11"
        opt_flags = " -O3 -march=native -g"

    all_flags = common_flags + opt_flags
    conf.env['CXXFLAGS'] = conf.env['CXXFLAGS'] + all_flags.split(' ')
    print conf.env['CXXFLAGS']


def build(bld):
    files = glob.glob(bld.path.abspath()+"/src/robot_dart/*.cpp")
    files = [f[len(bld.path.abspath())+1:] for f in files]
    robot_dart_srcs = " ".join(files)

    libs = 'BOOST EIGEN DART'
    libs_graphics = libs + ' DART_GRAPHIC'

    bld.program(features = 'cxx ' + bld.env['lib_type'],
                source = robot_dart_srcs,
                includes = './src',
                uselib = libs,
                target = 'RobotDARTSimu')

    if bld.get_env()['BUILD_GRAPHIC'] == True:
        bld.program(features = 'cxx',
                      install_path = None,
                      source = 'src/examples/pendulum_test.cpp',
                      includes = './src',
                      uselib = libs_graphics,
                      use = 'RobotDARTSimu',
                      defines = ['GRAPHIC'],
                      target = 'pendulum_test')

        bld.program(features = 'cxx',
                      install_path = None,
                      source = 'src/examples/arm_test.cpp',
                      includes = './src',
                      uselib = libs_graphics,
                      use = 'RobotDARTSimu',
                      defines = ['GRAPHIC'],
                      target = 'arm_test')

        # if we found the hexapod controller includes
        if len(bld.env.INCLUDES_HEXAPOD_CONTROLLER) > 0:
            bld.program(features = 'cxx',
                        install_path = None,
                        source = 'src/examples/hexapod.cpp',
                        includes = './src',
                        uselib = libs_graphics + ' HEXAPOD_CONTROLLER',
                        use = 'RobotDARTSimu',
                        defines = ['GRAPHIC'],
                        target = 'hexapod')

    bld.program(features = 'cxx',
                  install_path = None,
                  source = 'src/examples/pendulum_test.cpp',
                  includes = './src',
                  uselib = libs,
                  use = 'RobotDARTSimu',
                  target = 'pendulum_test_plain')

    bld.program(features = 'cxx',
                  install_path = None,
                  source = 'src/examples/arm_test.cpp',
                  includes = './src',
                  uselib = libs,
                  use = 'RobotDARTSimu',
                  target = 'arm_test_plain')

    # if we found the hexapod controller includes
    if len(bld.env.INCLUDES_HEXAPOD_CONTROLLER) > 0:
        bld.program(features = 'cxx',
                    install_path = None,
                    source = 'src/examples/hexapod.cpp',
                    includes = './src',
                    uselib = libs + ' HEXAPOD_CONTROLLER',
                    use = 'RobotDARTSimu',
                    target = 'hexapod_plain')

    install_files = glob.glob(bld.path.abspath()+"/src/robot_dart/*.hpp")
    install_files = [f[len(bld.path.abspath())+1:] for f in install_files]

    for f in install_files:
        bld.install_files('${PREFIX}/include/robot_dart', f)
    if bld.env['lib_type'] == 'cxxstlib':
        bld.install_files('${PREFIX}/lib', blddir + '/libRobotDARTSimu.a')
    else:
        bld.install_files('${PREFIX}/lib', blddir + '/libRobotDARTSimu.so')
    # bld.install_files('${PREFIX}/share/arm_models/URDF', 'res/models/arm.urdf')
