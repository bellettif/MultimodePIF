'''
Created on 2 Feb. 2015

compile with command line 
python setup.py build_ext --inplace

@author: francois belletti
'''

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

# For numpy array support
import numpy as np
import os

#os.environ["CC"] = "g++-4.9"
#os.environ["CXX"] = "g++-4.9"

external_filepath = "../../../XcodeWksp/k_shortest_threshold/k_shortest_threshold" 

sourcefiles = ["k_shortest_thr.pyx", 
				external_filepath + "/exec.cpp",
				external_filepath + "/geo_tools.cpp",]
main_I = "/usr/local/include"
main_L = ["-L/usr/local/lib"]

c11_args = ["-std=c++11"]#, "-stdlib=libstdc++"]

setup(
	cmdclass = {"build_ext" : build_ext},
	ext_modules = [Extension("k_shortest_thr_c",
			sourcefiles,
			include_dirs = [".",
							np.get_include(),
							main_I,
							external_filepath],
			language = "c++",
			extra_compile_args= c11_args + ["-O3"],
            extra_link_args=(main_L )
            )]
)
