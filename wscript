#!/usr/bin/env python
from waflib.extras import autowaf as autowaf
import re

# Variables for 'waf dist'
APPNAME = 'ir-cab-sim'
VERSION = '0.0.1'

# Mandatory variables
top = '.'
out = 'build'

def options(opt):
    opt.load('compiler_c')
    autowaf.set_options(opt)

def configure(conf):
    conf.load('compiler_c')
    autowaf.configure(conf)
    autowaf.set_c99_mode(conf)
    autowaf.display_header('LV2 IR Cab Sim')

    if not autowaf.is_child():
        autowaf.check_pkg(conf, 'lv2', uselib_store='LV2')

    conf.check(features='c cshlib', lib='m', uselib_store='M', mandatory=False)

    autowaf.display_msg(conf, 'LV2 bundle directory', conf.env.LV2DIR)
    print('')

def build(bld):
    bundle = 'ir-cab-sim'

    # Make a pattern for shared objects without the 'lib' prefix
    module_pat = re.sub('^lib', '', bld.env.cshlib_PATTERN)
    module_ext = module_pat[module_pat.rfind('.'):]

    # Build manifest.ttl by substitution (for portable lib extension)
    bld(features     = 'subst',
        source       = 'manifest.ttl.in',
        target       = '%s/%s' % (bundle, 'manifest.ttl'),
        install_path = '${LV2DIR}/%s' % bundle,
        LIB_EXT      = module_ext)

    # Copy other data files to build bundle (build/ir-cab-sim.lv2)
    for i in ['ir-cab-sim.ttl']:
        bld(features     = 'subst',
            is_copy      = True,
            source       = i,
            target       = '%s/%s' % (bundle, i),
            install_path = '${LV2DIR}/%s' % bundle)

    # Use LV2 headers from parent directory if building as a sub-project
    includes = None
    if autowaf.is_child:
        includes = '../..'

    # Build plugin library
    obj = bld(features     = 'c cshlib',
              source       = 'ir-cab-sim.c',
              name         = 'ir-cab-sim',
              target       = '%s/ir-cab-sim' % bundle,
              install_path = '${LV2DIR}/%s' % bundle,
              uselib       = 'M LV2',
              includes     = includes)
    obj.env.cshlib_PATTERN = module_pat
