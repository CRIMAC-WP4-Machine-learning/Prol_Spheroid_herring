import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# funcs -----------------------------------
def Get_Angle(_p0, _p1, _u_p1):
    ''' 
    Inputs:
    _p0 = np.array([x0, y0, z0])  observation point (coordinate of echosounder)
    _p1 = np.array([x1, y1, z1])  location of fish (coordinate of fish)
    _u_p1 = np.array([1.0, 1.0, 0.0])  #  (orientation at p1, unit vector) Orientation of the fish

    Outputs:
    '''
    # _p0 = np.array([0.0, 0.0, 5.0]) 
    # _p1 = np.array([0.0, 0.0, 0.0])
    # _u_p1 = np.array([1.0, 1.0, 0.0])  # orientation at p1

    _u_p1_norm = np.linalg.norm(_u_p1)  # unit vector (orientation at p1)


    v = _p0 - _p1
    v_norm = np.linalg.norm(v)

    # Ensure v is not zero-length
    if v_norm > 0:
        cos_theta = np.dot(_u_p1, v) / (v_norm*_u_p1_norm)
        # Clip for numerical stability
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        theta_rad = np.arccos(cos_theta)
        theta_deg = np.degrees(theta_rad)
        print(f"Angle: {theta_deg:.2f} degrees")
    else:
        print("Warning: p0 and p1 are the same point.")
# funcs -----------------------------------

# Example: place N points with no overlap
N = 100
a, b = 2.0, 0.6  # spheroid axes
points = []
min_dist = 0.2

while len(points) < N:
    x = np.random.uniform(-a, a)
    y = np.random.uniform(-b, b)
    z = np.random.uniform(-b, b)
    if (x**2/a**2 + y**2/b**2 + z**2/b**2) <= 1:
        p = np.array([x, y, z])
        if all(np.linalg.norm(p - q) > min_dist for q in points):
            points.append(p)

points = np.array(points)



# Random unit vectors: 
# "Theta" is the angle of projected vector on XY plane and X axis
# "Phi" is the angle of vector and Z axis
N = len(points)  # or however many vectors you need

# Generate arrays of theta and phi
theta = np.random.uniform(0, np.pi/6, size=N)
phi = np.random.uniform(np.pi/4, 3*np.pi/4, size=N)

# Convert spherical to Cartesian coordinates
x = np.sin(phi) * np.cos(theta)
y = np.sin(phi) * np.sin(theta)
z = np.cos(phi)

orientations = np.stack((x, y, z), axis=1)  # shape (N, 3)
orientations /= np.linalg.norm(orientations, axis=1)[:, np.newaxis]  # normalize


# Plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.quiver(points[:, 0], points[:, 1], points[:, 2],
          orientations[:, 0], orientations[:, 1], orientations[:, 2],
          length=0.3, normalize=True)

# Equal aspect ratio
max_range = np.array([
    points[:, 0].max() - points[:, 0].min(),
    points[:, 1].max() - points[:, 1].min(),
    points[:, 2].max() - points[:, 2].min()
]).max() / 2.0

mid_x = (points[:, 0].max() + points[:, 0].min()) * 0.5
mid_y = (points[:, 1].max() + points[:, 1].min()) * 0.5
mid_z = (points[:, 2].max() + points[:, 2].min()) * 0.5

ax.set_xlim(mid_x - max_range, mid_x + max_range)
ax.set_ylim(mid_y - max_range, mid_y + max_range)
ax.set_zlim(mid_z - max_range, mid_z + max_range)

plt.show()


 # ======================================================
# Angle between "u" the unit vector of point "p1" and vector connecting "p0" to "p1":
print('points[0], orientations[0]: ', points[0], orientations[0])

p0 = np.array([0.0, 0.0, 5.0]) 
p1 = np.array([0.0, 0.0, 0.0])
u_p1 = np.array([0.0, 1.0, 1.0])  # orientation at p1
Get_Angle(p0, p1, u_p1)

print('np.linalg.norm(p1-p0): ', np.linalg.norm(p1-p0))
