# Vectors and Vector Operations (Linear Algebra)

## Definitions
- **Vector ($\vec{v}$)**: A mathematical object with both magnitude (length) and direction.
- **Components**: A vector in 2D or 3D can be represented as $\vec{v} = \langle v_1, v_2, v_3 \rangle$ or $\vec{v} = v_1\hat{i} + v_2\hat{j} + v_3\hat{k}$.
- **Magnitude ($||\vec{v}||$)**: The "length" of the vector. 
  $||\vec{v}|| = \sqrt{v_1^2 + v_2^2 + v_3^2}$
- **Unit Vector ($\hat{u}$)**: A vector with a magnitude of 1 in the same direction as $\vec{v}$.
  $\hat{u} = \frac{\vec{v}}{||\vec{v}||}$

## Basic Operations
- **Vector Addition**: Add corresponding components: $\vec{u} + \vec{v} = \langle u_1+v_1, u_2+v_2, u_3+v_3 \rangle$.
- **Scalar Multiplication**: Multiply each component by a scalar $c$: $c\vec{v} = \langle cv_1, cv_2, cv_3 \rangle$.

## The Dot Product (Scalar Product)
The dot product takes two vectors and returns a **single scalar number**.
**Algebraic formula**: $\vec{u} \cdot \vec{v} = u_1v_1 + u_2v_2 + u_3v_3$
**Geometric formula**: $\vec{u} \cdot \vec{v} = ||\vec{u}|| \cdot ||\vec{v}|| \cos(\theta)$ (where $\theta$ is the angle between them).

### Key Application: Orthogonality
If $\vec{u} \cdot \vec{v} = 0$, then the two vectors are **orthogonal (perpendicular)**.

## The Cross Product (Vector Product)
The cross product takes two 3D vectors and returns a **new vector** that is orthogonal to both original vectors.
**Formula**: 
For $\vec{u} = \langle u_1, u_2, u_3 \rangle$ and $\vec{v} = \langle v_1, v_2, v_3 \rangle$:
$$\vec{u} \times \vec{v} = \langle (u_2v_3 - u_3v_2), -(u_1v_3 - u_3v_1), (u_1v_2 - u_2v_1) \rangle$$
(This is efficiently calculated as the determinant of a 3x3 matrix with $\hat{i}, \hat{j}, \hat{k}$ in the top row).

### Geometric Meaning
$||\vec{u} \times \vec{v}|| = ||\vec{u}|| \cdot ||\vec{v}|| \sin(\theta)$
This magnitude is exactly equal to the **Area of the parallelogram** spanned by the two vectors.

## Common Mistakes
- **Confusing outputs**: The dot product results in a scalar (number). The cross product results in a vector.
- **Cross product in 2D**: The cross product is only defined for 3-dimensional vectors space.
- **Commutativity of Cross Product**: The cross product is NOT commutative! $\vec{u} \times \vec{v} = -(\vec{v} \times \vec{u})$.
