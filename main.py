import json
import os
import sys

def muat_basis_pengetahuan(nama_file="kb_wifi.json"):
    direktori_skrip = os.path.dirname(os.path.abspath(__file__))
    path_file = os.path.join(direktori_skrip, nama_file)

    if not os.path.exists(path_file):
        path_file = nama_file

    if not os.path.exists(path_file):
        print(f"Error: File '{nama_file}' tidak ditemukan.")
        sys.exit(1)

    with open(path_file, "r", encoding="utf-8") as f:
        return json.load(f)

def cari_fakta_dasar(aturan):
    semua_hasil = {r["maka"] for r in aturan}
    fakta_dasar = []
    fakta_tercatat = set()

    for r in aturan:
        for syarat in r["jika"]:
            if syarat not in semua_hasil and syarat not in fakta_tercatat:
                fakta_dasar.append(syarat)
                fakta_tercatat.add(syarat)
    return fakta_dasar

def tanyakan_user(fakta_dasar):
    memori = set()
    print("Jawab pertanyaan berikut dengan 'y' (ya) atau 't' (tidak):\n")
    for i, fakta in enumerate(fakta_dasar, 1):
        while True:
            jawaban = input(f"{i}. Apakah {fakta}? (y/t) > ").strip().lower()
            if jawaban in ["y", "ya"]:
                memori.add(fakta)
                break
            elif jawaban in ["t", "tidak"]:
                break
            else:
                print("   [Pilihan tidak valid, mohon masukkan 'y' atau 't']")
    return memori

def forward_chaining(aturan, memori_awal):
    memori = set(memori_awal)
    riwayat_alasan = {}
    siklus = 1
    log_siklus = []

    while True:
        aturan_cocok = []
        for r in aturan:
            if r["maka"] in memori:
                continue

            if r["mode"] == "dan":
                terpenuhi = all(syarat in memori for syarat in r["jika"])
                premis_aktif = r["jika"] if terpenuhi else []
            elif r["mode"] == "atau":
                premis_aktif = [s for s in r["jika"] if s in memori]
                terpenuhi = len(premis_aktif) > 0
            else:
                terpenuhi = False
                premis_aktif = []

            if terpenuhi:
                aturan_cocok.append((r, premis_aktif))

        if not aturan_cocok:
            log_siklus.append(f"Siklus {siklus}: tidak ada aturan baru, inferensi selesai.")
            break

        r, premis_aktif = aturan_cocok[0]
        memori.add(r["maka"])
        riwayat_alasan[r["maka"]] = (r["id"], premis_aktif, r.get("sumber", "-"))
        log_siklus.append(f"Siklus {siklus}: {r['id']} -> {r['maka']}")
        siklus += 1

    return memori, riwayat_alasan, log_siklus

def cetak_pohon_alasan(target, riwayat_alasan, indent=2):
    if target not in riwayat_alasan:
        return
    r_id, premis, sumber = riwayat_alasan[target]
    spasi = " " * indent
    premis_str = ", ".join(premis)
    print(f"{spasi}{target}  <- {r_id} ({premis_str}) [Sumber: {sumber}]")
    for p in premis:
        if p in riwayat_alasan:
            cetak_pohon_alasan(p, riwayat_alasan, indent + 4)

def main():
    kb = muat_basis_pengetahuan("kb_wifi.json")
    print("=" * 70)
    print(f" {kb.get('judul', 'Sistem Pakar')} ")
    print("=" * 70)

    fakta_dasar = cari_fakta_dasar(kb["aturan"])
    fakta_awal = tanyakan_user(fakta_dasar)

    print("\n" + "-" * 70)
    if fakta_awal:
        print("Fakta awal yang terdeteksi:")
        for f in fakta_awal:
            print(f" - {f}")
    else:
        print("Fakta awal: Tidak ada kondisi gangguan yang dipilih.")
    print("-" * 70 + "\n")

    memori_akhir, riwayat_alasan, log_siklus = forward_chaining(kb["aturan"], fakta_awal)

    for log in log_siklus:
        print(log)
    print()

    fakta_perantara = set()
    for r in kb["aturan"]:
        for s in r["jika"]:
            if s in riwayat_alasan:
                fakta_perantara.add(s)

    kesimpulan_akhir = [f for f in riwayat_alasan.keys() if f not in fakta_perantara]

    print("=" * 70)
    if kesimpulan_akhir:
        print("HASIL DIAGNOSIS / KESIMPULAN:")
        for k in kesimpulan_akhir:
            print(f" * {k.upper()}")
        
        print("\nALASAN & RUNUTAN ATURAN (CHAIN OF REASONING):")
        for k in kesimpulan_akhir:
            cetak_pohon_alasan(k, riwayat_alasan)
    else:
        print("HASIL DIAGNOSIS: Tidak ada kesimpulan yang cocok.")
        print("Alasan: Pola gejala yang Anda masukkan tidak memenuhi prasyarat aturan diagnosis yang tersedia.")
    print("=" * 70)

    print("\nCATATAN BATAS KEBERLAKUAN:")
    print(kb.get("batas", "-"))
    print("=" * 70)

if __name__ == "__main__":
    main()
