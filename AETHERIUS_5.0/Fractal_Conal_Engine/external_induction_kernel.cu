# ===== FILE: external_induction_kernel.cu =====
# Author: Jonathan Wayne Fleuren (Aetherius Cognitive Systems) & Antigravity (Autonomous Pair AI Engine)
# Date: July 2026

// ===== FILE: pure_math_engine/cuda_conal_kernels/external_induction_kernel.cu =====
/*
 * Custom CUDA C++ Kernel for External Vector Field Induction Forces F_ext (PMCA Generation 4.0)
 * Computes inward induction vectors F_ext(p_i) = sum (v_k - p_i) / (||v_k - p_i||^2 + eps)
 */

#include <torch/extension.h>
#include <cuda.h>
#include <cuda_runtime.h>
#include <math.h>

__global__ void external_field_induction_cuda_kernel(
    const float* __restrict__ P,       // Inner State Points (N x 3)
    const float* __restrict__ V,       // Outer Casing Vectors (K x 3)
    float* __restrict__ F_out,         // Resultant Induction Force Vectors (N x 3)
    const int N,
    const int K,
    const float epsilon
) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    if (i < N) {
        float px = P[i * 3 + 0];
        float py = P[i * 3 + 1];
        float pz = P[i * 3 + 2];

        float fx = 0.0f;
        float fy = 0.0f;
        float fz = 0.0f;

        for (int k = 0; k < K; ++k) {
            float vx = V[k * 3 + 0];
            float vy = V[k * 3 + 1];
            float vz = V[k * 3 + 2];

            float dx = vx - px;
            float dy = vy - py;
            float dz = vz - pz;

            float dist_sq = dx * dx + dy * dy + dz * dz + epsilon;
            float inv_dist = 1.0f / dist_sq;

            fx += dx * inv_dist;
            fy += dy * inv_dist;
            fz += dz * inv_dist;
        }

        F_out[i * 3 + 0] = fx;
        F_out[i * 3 + 1] = fy;
        F_out[i * 3 + 2] = fz;
    }
}

torch::Tensor external_field_induction_cuda(
    torch::Tensor P,
    torch::Tensor V,
    float epsilon
) {
    const int N = P.size(0);
    const int K = V.size(0);

    auto F_out = torch::zeros_like(P);

    const int threads_per_block = 256;
    const int blocks_per_grid = (N + threads_per_block - 1) / threads_per_block;

    external_field_induction_cuda_kernel<<<blocks_per_grid, threads_per_block>>>(
        P.data_ptr<float>(),
        V.data_ptr<float>(),
        F_out.data_ptr<float>(),
        N,
        K,
        epsilon
    );

    return F_out;
}
