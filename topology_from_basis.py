T = Topologie.aus_basis(
    grundmenge={1, 2, 3},
    basis=[
        {1},
        {1, 2},
        {1, 2, 3},
    ],
)

print(T)
print(T.offene_mengen)
