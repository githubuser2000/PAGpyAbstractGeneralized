T = Topologie(
    grundmenge={1, 2, 3},
    offene_mengen=[
        set(),
        {1, 2, 3},
        {1},
        {1, 2},
    ],
)

print(T.offene_mengen)
print("inneres({1,3}) =", T.inneres({1, 3}))
print("abschluss({3}) =", T.abschluss({3}))
print("rand({1}) =", T.rand({1}))
print("umgebungen von 1 =", T.umgebungen(1))
