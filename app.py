import os
from flask import Flask, render_template, request
import pandas as pd
import numpy as np

app = Flask(__name__)

DOSYA_HARITASI = {
    "Süper Lig": "super_lig_tum_sezonlar.xlsx",
    "Premier Lig": "premier_lig_tum_sezonlar.xlsx",
    "La Liga": "laliga_tum_sezonlar.xlsx",
    "Serie A": "serie_a_tum_sezonlar.xlsx",
    "MLS": "mls_tum_sezonlar.xlsx"
}

@app.route("/", methods=["GET", "POST"])
def index():
    rapor = None
    if request.method == "POST":
        secilen_lig = request.form.get("lig")
        takim1 = request.form.get("takim1", "").strip()
        takim2 = request.form.get("takim2", "").strip()
        
        try:
            m1_hedef = float(request.form.get("m1"))
            m0_hedef = float(request.form.get("m0"))
            m2_hedef = float(request.form.get("m2"))
        except ValueError:
            return render_template("index.html", rapor="Hata: Lütfen oranları sayısal formatta girin.")

        dosya = DOSYA_HARITASI.get(secilen_lig, "super_lig_tum_sezonlar.xlsx")
        
        if not os.path.exists(dosya):
            return render_template("index.html", rapor=f"Hata: '{dosya}' dosyası sunucuda bulunamadı!")

        df = pd.read_excel(dosya)
        df_filtered = df.copy()
        
        if takim1 and takim2:
            df_filtered = df_filtered[
                df_filtered['Ev_Sahibi'].astype(str).str.contains(takim1, case=False, na=False) | 
                df_filtered['Deplasman'].astype(str).str.contains(takim1, case=False, na=False) |
                df_filtered['Ev_Sahibi'].astype(str).str.contains(takim2, case=False, na=False) | 
                df_filtered['Deplasman'].astype(str).str.contains(takim2, case=False, na=False)
            ]
        elif takim1:
            df_filtered = df_filtered[
                df_filtered['Ev_Sahibi'].astype(str).str.contains(takim1, case=False, na=False) | 
                df_filtered['Deplasman'].astype(str).str.contains(takim1, case=False, na=False)
            ]
        elif takim2:
            df_filtered = df_filtered[
                df_filtered['Ev_Sahibi'].astype(str).str.contains(takim2, case=False, na=False) | 
                df_filtered['Deplasman'].astype(str).str.contains(takim2, case=False, na=False)
            ]

        df_clean = df_filtered.dropna(subset=['MS1', 'MS0', 'MS2']).drop_duplicates(
            subset=['Sezon', 'Ev_Sahibi', 'Deplasman', 'Skor', 'MS1', 'MS0', 'MS2']
        ).copy()
        
        if df_clean.empty:
            return render_template("index.html", rapor="Kriterlere uygun eşleşen veri bulunamadı.")

        def calculate_universal_distance(row):
            m1, m0, m2 = row['MS1'], row['MS0'], row['MS2']
            w1 = 4.0 if m1_hedef < 1.30 else (1.5 if m1_hedef < 2.20 else 1.0)
            w0 = 1.5 if m0_hedef > 5.0 else 1.0
            w2 = 2.0 if m2_hedef > 5.0 else 1.0
            
            d1 = w1 * abs(m1 - m1_hedef) / max(m1_hedef, 1.0)
            d2 = w0 * abs(m0 - m0_hedef) / max(m0_hedef, 1.0)
            d3 = w2 * abs(m2 - m2_hedef) / max(m2_hedef, 1.0)
            return np.sqrt(d1**2 + d2**2 + d3**2)

        df_clean['sapma_skoru'] = df_clean.apply(calculate_universal_distance, axis=1)
        
        filtrelenmis = pd.DataFrame()
        tolerans_adim = 0.20
        max_tolerans_siniri = 1.00
        
        while filtrelenmis.empty and tolerans_adim <= max_tolerans_siniri:
            filtrelenmis = df_clean[df_clean['sapma_skoru'] <= tolerans_adim]
            if filtrelenmis.empty:
                tolerans_adim += 0.15

        sonuclar = filtrelenmis.sort_values('sapma_skoru').copy()
        
        if sonuclar.empty:
            return render_template("index.html", rapor="Bu oranlara yakın hiçbir maç bulunamadı.")
            
        sonuclar['Sonuc'] = np.select(
            [sonuclar['Ev_Gol'] > sonuclar['Dep_Gol'], sonuclar['Ev_Gol'] == sonuclar['Dep_Gol']],
            ['MS1', 'MS0'],
            default='MS2'
        )
        
        toplam_mac = len(sonuclar)
        ms1_sayi = (sonuclar['Sonuc'] == 'MS1').sum()
        ms0_sayi = (sonuclar['Sonuc'] == 'MS0').sum()
        ms2_sayi = (sonuclar['Sonuc'] == 'MS2').sum()
        
        if takim1 and takim2:
            baslik_etiket = f"{takim1.upper()} veya {takim2.upper()} ({secilen_lig})"
        elif takim1:
            baslik_etiket = f"{takim1.upper()} ({secilen_lig})"
        elif takim2:
            baslik_etiket = f"{takim2.upper()} ({secilen_lig})"
        else:
            baslik_etiket = f"GENEL LİG ANALİZİ ({secilen_lig})"
        
        rapor_metni = []
        rapor_metni.append(f"{'='*68}")
        rapor_metni.append(f" {baslik_etiket} | Toplam Maç: {toplam_mac} | Tolerans: {tolerans_adim:.2f}")
        rapor_metni.append(f"{'='*68}")
        rapor_metni.append(f" Ev Sahibi Kazanma (MS1) : {ms1_sayi} adet (%{ms1_sayi/toplam_mac*100:.1f})")
        rapor_metni.append(f" Beraberlik (MS0)        : {ms0_sayi} adet (%{ms0_sayi/toplam_mac*100:.1f})")
        rapor_metni.append(f" Deplasman Kazanma (MS2) : {ms2_sayi} adet (%{ms2_sayi/toplam_mac*100:.1f})")
        rapor_metni.append("\n En Sık Görülen Skorlar:")
        for skor, adet in sonuclar['Skor'].value_counts().head(3).items():
            rapor_metni.append(f"   - {skor} ({adet} kez)")
        rapor_metni.append(f"{'='*68}")
        rapor_metni.append(" Eşleşen Tüm Benzer Maçlar:")
        rapor_metni.append(sonuclar[['Sezon', 'Ev_Sahibi', 'Deplasman', 'Skor', 'MS1', 'MS0', 'MS2', 'sapma_skoru']].to_string(index=False))
        
        rapor = "\n".join(rapor_metni)
        return render_template("index.html", rapor=rapor)

    return render_template("index.html", rapor=None)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)