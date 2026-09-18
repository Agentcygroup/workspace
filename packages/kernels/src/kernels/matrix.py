def matmul(A, B):
    if not A or not B:
        raise ValueError("empty matrix")
    n = len(A); m = len(A[0]); p = len(B); q = len(B[0])
    if m != p:
        raise ValueError("shape mismatch")
    C = [[0.0]*q for _ in range(n)]
    for i in range(n):
        for k in range(m):
            a = A[i][k]
            for j in range(q):
                C[i][j] += a * B[k][j]
    return C
