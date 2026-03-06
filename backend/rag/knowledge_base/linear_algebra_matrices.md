# Matrices and Matrix Operations (Linear Algebra)

## Definitions
- **Matrix**: A rectangular array of numbers arranged in rows ($m$) and columns ($n$). Its dimensions are $m \times n$.
- **Element $a_{ij}$**: The entry in the $i$-th row and $j$-th column.
- **Identity Matrix ($I$)**: A square matrix with $1$s on the main diagonal and $0$s elsewhere. $AI = IA = A$.
- **Transpose ($A^T$)**: Formed by swapping rows and columns. The $i$-th row becomes the $i$-th column.

## Matrix Operations

### 1. Addition and Subtraction
- Matrices can only be added or subtracted if they share the **exact same dimensions**.
- To add $A + B$, add corresponding elements: $c_{ij} = a_{ij} + b_{ij}$.

### 2. Scalar Multiplication
- Multiply every element in the matrix by a constant scalar $k$.
- $(kA)_{ij} = k \cdot a_{ij}$.

### 3. Matrix Multiplication ($AB$)
- The number of **columns of A** must equal the number of **rows of B**.
- If $A$ is $m \times n$ and $B$ is $n \times p$, then $C = AB$ is an $m \times p$ matrix.
- Element $c_{ij}$ is the dot product of the $i$-th row of $A$ and the $j$-th column of $B$.
- **Note: Matrix multiplication is generally NOT commutative!** ($AB \neq BA$).

## Determinant of a Matrix ($det(A)$ or $|A|$)
Only defined for square matrices.

### 2x2 Matrix
For $A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}$, the determinant is $|A| = ad - bc$.

### Singular vs Non-Singular
- If $det(A) = 0$, the matrix is **Singular** (it has no inverse).
- If $det(A) \neq 0$, the matrix is **Non-Singular** (it has an inverse).

## The Inverse of a Matrix ($A^{-1}$)
A square matrix $A$ has an inverse such that $AA^{-1} = A^{-1}A = I$.
For a 2x2 matrix $A = \begin{pmatrix} a & b \\ c & d \end{pmatrix}$:
$$A^{-1} = \frac{1}{ad - bc} \begin{pmatrix} d & -b \\ -c & a \end{pmatrix}$$

## Solving Systems with Matrices
A linear system can be represented as $AX = B$.
If $A$ is non-singular, you can solve for $X$ using:
$$X = A^{-1}B$$

## Common Mistakes
- **Multiplying non-conformable matrices**: Attempting to calculate $AB$ when the inner dimensions don't match.
- **Assuming $AB = BA$**: This is usually false.
- **Dividing by matrices**: You cannot "divide" by a matrix! You must multiply by its inverse.
- **Applying inverse formula to singular matrices**: You cannot find the inverse if $ad - bc = 0$.
