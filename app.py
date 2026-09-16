import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import pandas as pd


class FutbolAnalizApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Futbol Maç Analiz Sistemi - 2026/2027")
    self.root.geometry("750x650")
    self.root.config(bg="#f4f6f9")

    # Stil Ayarları
    style = ttk.Style()
    style.theme_use("clam")

    # Başlık
    title_label = tk.Label(
        root,
        text="Futbol Maç Analiz & İstatistik Otomasyonu",
        font=("Arial", 16, "bold"),
        bg="#f4f6f9",
        fg="#2c3e50",
    )
    title_label.pack(pady=15)

    # Ana Çerçeve
    main_frame = tk.Frame(root, bg="#f4f6f9")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20)

    # --- GİRİŞ ALANLARI ÇERÇEVESİ ---
    input_frame = tk.LabelFrame(
        main_frame,
        text=" Maç ve Oran Parametreleri ",
        font=("Arial", 11, "bold"),
        bg="#f4f6f9",
        fg="#34495e",
        padx=15,
        pady=15,
    )
    input_frame.pack(fill=tk.X, pady=5)

    # Takım 1
    tk.Label(
        input_frame,
        text="Ev Sahibi / 1. Takım:",
        font=("Arial", 10),
        bg="#f4f6f9",
    ).grid(row=0, column=0, sticky="w", pady=5)
    self.entry_takim1 = tk.Entry(input_frame, font=("Arial", 10), width=25)
    self.entry_takim1.grid(row=0, column=1, padx=10, pady=5)

    # Takım 2
    tk.Label(
        input_frame,
        text="Deplasman / 2. Takım:",
        font=("Arial", 10),
        bg="#f4f6f9",
    ).grid(row=1, column=0, sticky="w", pady=5)
    self.entry_takim2 = tk.Entry(input_frame, font=("Arial", 10), width=25)
    self.entry_takim2.grid(row=1, column=1, padx=10, pady=5)

    # Oran Giriş Alanı
    tk.Label(
        input_frame,
        text="Maç Oranları / Eşik Değer:",
        font=("Arial", 10),
        bg="#f4f6f9",
    ).grid(row=2, column=0, sticky="w", pady=5)
    self.entry_oran = tk.Entry(input_frame, font=("Arial", 10), width=25)
    self.entry_oran.grid(row=2, column=1, padx=10, pady=5)

    # --- BUTONLAR ---
    btn_frame = tk.Frame(main_frame, bg="#f4f6f9")
    btn_frame.pack(fill=tk.X, pady=10)

    self.btn_analiz = tk.Button(
        btn_frame,
        text="Analizi Başlat",
        font=("Arial", 11, "bold"),
        bg="#27ae60",
        fg="white",
        width=18,
        command=self.analiz_yap,
    )
    self.btn_analiz.pack(side=tk.LEFT, padx=5)

    self.btn_temizle = tk.Button(
        btn_frame,
        text="Formu Temizle",
        font=("Arial", 11),
        bg="#c0392b",
        fg="white",
        width=15,
        command=self.formu_temizle,
    )
    self.btn_temizle.pack(side=tk.LEFT, padx=5)

    # --- SONUÇ / ÇIKTI ALANI ---
    output_frame = tk.LabelFrame(
        main_frame,
        text=" Benzer Maçlar ve İstatistik Sonuçları ",
        font=("Arial", 11, "bold"),
        bg="#f4f6f9",
        fg="#34495e",
        padx=10,
        pady=10,
    )
    output_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    self.text_sonuc = tk.Text(
        output_frame,
        font=("Consolas", 10),
        bg="white",
        fg="#2c3e50",
        height=15,
    )
    self.text_sonuc.pack(fill=tk.BOTH, expand=True)

    # Örnek başlangıç verisi doldurma (Test için)
    self.ornek_verileri_yukle()

  def ornek_verileri_yukle(self):
    # Otomatik çekilen veya güncel lig takımlarını simüle eden başlangıç doldurması
    self.entry_takim1.insert(0, "Arsenal")
    self.entry_takim2.insert(0, "Manchester City")
    self.entry_oran.insert(0, "1.72")

  def analiz_yap(self):
    t1 = self.entry_takim1.get()
    t2 = self.entry_takim2.get()
    oran = self.entry_oran.get()

    if not t1 or not t2:
      messagebox.showwarning(
          "Eksik Bilgi", "Lütfen takım isimlerini kontrol edin."
      )
      return

    # Pandas / Numpy ile analiz simülasyonu
    # (Buraya kendi veri işleme ve pandas filtreleme kodlarınızı entegre edebilirsiniz)
    veriler = {
        "Lig": ["TR 2026/2027", "TR 2026/2027", "TR 2026/2027"],
        "Ev Sahibi": [t1, "Galatasaray", t2],
        "Deplasman": [t2, "Fenerbahçe", "Beşiktaş"],
        "Oran": [oran, "1.80", "1.65"],
        "KG": ["Var", "Yok", "Var"],
        "2.5 Üst": ["Evet", "Hayır", "Evet"],
    }
    df = pd.DataFrame(veriler)

    # Sonuç ekranını temizle ve yeni sonuçları yaz
    self.text_sonuc.delete("1.0", tk.END)
    self.text_sonuc.insert(
        tk.END,
        f"--- {t1} vs {t2} İçin Benzer Maç Analiz Raporu ---\n"
        f"Kullanılan Oran / Eşik: {oran}\n\n",
    )
    self.text_sonuc.insert(tk.END, df.to_string(index=False))

    # NOT: BURADA GİRDİ KUTULARI SIFIRLANMIYOR.
    # Böylece yazdığınız takım ve oranlar ekranda sabit kalıyor.

  def formu_temizle(self):
    # Sadece kullanıcı "Formu Temizle" butonuna basarsa kutular sıfırlanır
    self.entry_takim1.delete(0, tk.END)
    self.entry_takim2.delete(0, tk.END)
    self.entry_oran.delete(0, tk.END)
    self.text_sonuc.delete("1.0", tk.END)


if __name__ == "__main__":
  root = tk.Tk()
  app = FutbolAnalizApp(root)
  root.mainloop()
