import multiprocessing as mp
import time

import numpy as np

# Problem settings
N = 100  # Grid size (N x N)
iterations = 500  # Number of iterations
TOL = 1e-4  # Convergence tolerance
num_processes = mp.cpu_count()  # Use all available CPU cores

# Initialize the grid
phi = np.zeros((N, N))

# Boundary Conditions
phi[:, 0] = 100  # Left boundary = 100
phi[:, -1] = 100  # Right boundary = 100
phi[0, :] = 0  # Top boundary = 0
phi[-1, :] = 0  # Bottom boundary = 0


# Function to update part of the grid
def update_chunk(start_row, end_row, old_phi):
	new_phi = old_phi.copy()
	for i in range(start_row, end_row):
		for j in range(1, N - 1):  # Exclude boundaries
			new_phi[i, j] = 0.25 * (old_phi[i + 1, j] + old_phi[i - 1, j] + old_phi[i, j + 1] + old_phi[i, j - 1])
	return new_phi[start_row:end_row, :]


# Function to run the parallel computation
def parallel_jacobi(phi, iterations):
	chunk_size = (N - 2) // num_processes  # Divide rows among processes
	pool = mp.Pool(processes=num_processes)

	for _ in range(iterations):
		tasks = []
		for p in range(num_processes):
			start_row = 1 + p * chunk_size
			end_row = start_row + chunk_size
			if p == num_processes - 1:  # Ensure last chunk covers remaining rows
				end_row = N - 1
			tasks.append(pool.apply_async(update_chunk, (start_row, end_row, phi)))

		# Collect results and update the grid
		for p, task in enumerate(tasks):
			start_row = 1 + p * chunk_size
			end_row = start_row + chunk_size
			if p == num_processes - 1:
				end_row = N - 1
			phi[start_row:end_row, :] = task.get()

	pool.close()
	pool.join()
	return phi


# Run sequential solver for comparison
def sequential_jacobi(phi, iterations):
	for _ in range(iterations):
		new_phi = phi.copy()
		for i in range(1, N - 1):
			for j in range(1, N - 1):
				new_phi[i, j] = 0.25 * (phi[i + 1, j] + phi[i - 1, j] + phi[i, j + 1] + phi[i, j - 1])
		phi = new_phi
	return phi


# Time measurement
start_seq = time.time()
phi_seq = sequential_jacobi(phi.copy(), iterations)
end_seq = time.time()

start_par = time.time()
phi_par = parallel_jacobi(phi.copy(), iterations)
end_par = time.time()

# Print results
print(f'Time (Sequential): {end_seq - start_seq:.4f} seconds')
print(f'Time (Parallel):   {end_par - start_par:.4f} seconds')
print(f'Speedup Factor:    {(end_seq - start_seq) / (end_par - start_par):.2f}x')
