# ===== FILE: pure_math_engine/cuda_conal_kernels/setup.py =====
# Author: Jonathan Wayne Fleuren (Aetherius Cognitive Systems) & Antigravity (Autonomous Pair AI Engine)
# Date: July 2026
"""
PyTorch C++ CUDA Extension Build Script for PMCA Conal Metric Kernels
Build command: python setup.py build_ext --inplace
"""

from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name='pmca_cuda_kernels',
    ext_modules=[
        CUDAExtension(
            name='pmca_cuda_kernels',
            sources=[
                os.path.join(curr_dir, 'pybind_bridge.cpp'),
                os.path.join(curr_dir, 'conal_metric_kernel.cu'),
                os.path.join(curr_dir, 'external_induction_kernel.cu'),
                os.path.join(curr_dir, 'dynamic_manifold_warp_kernel.cu')
            ],
            extra_compile_args={
                'cxx': ['-O3'],
                'nvcc': ['-O3', '--use_fast_math']
            }
        )
    ],
    cmdclass={
        'build_ext': BuildExtension
    }
)