T = Topologie.diskrete_topologie({"a", "b", "c"})
print(T.ist_offen({"a"}))
print(T.ist_abgeschlossen({"a"}))
print(T.ist_diskret())
