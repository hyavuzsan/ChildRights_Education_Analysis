import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
import sys
import logging
import warnings

# Plotly hatasını sustur
sys.stderr = open('nul', 'w')

# CmdStanpy ve Prophet uyarılarını kapat
logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
logging.getLogger("prophet").setLevel(logging.ERROR)

# FutureWarning mesajlarını kapat
warnings.simplefilter(action='ignore', category=FutureWarning)

# Dosya yolunu belirt
file_path = r"C:\Users\Lenovo\Desktop\PythonProject4\src\NetAttendence.xlsx"
sheets = ["One year before", "Primary", "Lower secondary", "Upper secondary"]

# Tüm sekmeleri oku ve birleştir
data_frames = []
for sheet in sheets:
    df = pd.read_excel(file_path, sheet_name=sheet)
    df["Education Level"] = sheet  # Sekme adını bir sütun olarak ekle
    data_frames.append(df)

# Verileri birleştir
data = pd.concat(data_frames, ignore_index=True)

# Sütun adlarındaki boşlukları kaldır
data.columns = [str(col).replace(" ", "") for col in data.columns]

unnamed_cols = [col for col in data.columns if "Unnamed" in str(col)]
data.drop(columns=unnamed_cols, inplace=True)

# Gerekli sütunları yeniden adlandır
data.rename(columns={
    "Country": "Country",
    "Region": "Region",
    "EducationLevel": "Education Level",
    "Total": "Value",
}, inplace=True)

# Gerekli sütunları seç
required_columns = ["Country", "Region", "Education Level", "Value"]
if all(col in data.columns for col in required_columns):
    data = data[required_columns]
else:
    print("Hatalı sütun adları veya eksik sütunlar. Lütfen kontrol edin.")
    print("Mevcut sütunlar:", data.columns)
    exit()

# `Value` sütununu sayısal hale getir ve hataları kaldır
data["Value"] = pd.to_numeric(data["Value"], errors="coerce")
data.dropna(subset=["Value"], inplace=True)

region_mapping = {
    "EAP": "Doğu Asya ve Pasifik",
    "ECA": "Avrupa ve Orta Asya",
    "MENA": "Orta Doğu ve Kuzey Afrika",
    "SSA": "Sahra Altı Afrika",
    "LAC": "Latin Amerika ve Karayipler",
    "SA": "Güney Asya"
}
data["Region"] = data["Region"].map(region_mapping)

# İstenilen bölgeleri filtrele
desired_regions = list(region_mapping.values())
data = data[data["Region"].isin(desired_regions)]

# Kıtalar bazında çubuk grafik için veri hazırlığı
mean_values = data.groupby(["Region", "Education Level"])['Value'].mean().unstack()


while True:
    print("Hangi grafiği incelemek istiyorsunuz?")
    print("1) Kıtalar Bazında Eğitime Katılım Oranları (Ortalama)")
    print("2) Kıtalar Bazında Eğitime Katılım Oranları Dağılımı")
    for i, region in enumerate(desired_regions, start=3):
        print(f"{i}) {region} bölgesindeki ülkelerin katılım oranı")
    print("9) Dünya genelinde tahmini ilkokul bitirme oranlarını göster")
    choice = input("Lütfen bir seçenek girin (Çıkış için 'q'): ")


    if choice.lower() == 'q':
        break
    elif choice == "1":
        # Kıtalar bazında eğitime katılım oranlarını gruplandır ve eğitim seviyelerine göre dağıt
        mean_values = data.groupby(["Region", "Education Level"])["Value"].mean().unstack()


        if mean_values.isna().sum().sum() > 0:
            print("Dikkat: Veri setinde bazı eksik kategoriler olabilir!")

        # Bar chart oluştur
        ax = mean_values.plot(kind="bar", figsize=(14, 8), edgecolor="black", width=0.8)

        # Grafik ayarları
        ax.set_xlabel("Kıtalar")
        ax.set_ylabel("Katılım Oranı (%)")
        ax.set_title("Kıtalar Bazında Eğitime Katılım Oranları (Ortalama)")
        plt.xticks(rotation=45)
        plt.legend(title="Eğitim Seviyesi")
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        plt.subplots_adjust(bottom=0.25)  # Alt kısımdaki boşluğu artır
        plt.show()



    elif choice == "2":
        total_values = data.groupby("Region")["Value"].mean()
        total_values.plot(kind="pie", autopct="%1.1f%%", startangle=90, figsize=(8, 8), colormap="viridis")
        plt.title("Kıtalar Bazında Eğitime Katılım Oranları Dağılımı")
        plt.ylabel("")
        plt.show()

    elif choice.isdigit() and 3 <= int(choice) <= 2 + len(desired_regions):
        region_index = int(choice) - 3
        region = desired_regions[region_index]
        region_data = data[data["Region"] == region]

        if region_data.empty:
            print(f"{region} bölgesi için veri bulunamadı.")
        else:
            # Kıtaları ülkeler arasından çıkarıyoruz
            continent_names = [
                "East Asia & Pacific", "Europe & Central Asia", "Latin America & Caribbean",
                "Middle East & North Africa", "South Asia", "Sub-Saharan Africa"
            ]

            # Ülkeleri kıtalardan ayır
            filtered_data = region_data[~region_data["Country"].isin(continent_names)]

            # Ülkeler bazında ortalamayı hesapla
            mean_values = filtered_data.groupby("Country")["Value"].mean()

            # Görselleştirme
            plt.figure(figsize=(14, 7))
            mean_values.plot(kind="bar", color="coral", edgecolor="black")
            plt.title(f"{region} Bölgesindeki Ülkelerin Katılım Oranı", fontsize=16)
            plt.xlabel("Ülkeler", fontsize=12)
            plt.ylabel("Katılım Oranı (%)", fontsize=12)
            plt.xticks(rotation=45, ha="right", fontsize=10)
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()
            plt.show()


    elif choice == "9":

        # CmdStanpy ve FutureWarning mesajlarını kapat
        logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
        warnings.simplefilter(action='ignore', category=FutureWarning)


        file_path = r"C:\Users\Lenovo\Desktop\PythonProject4\src\Data.csv"

        df = pd.read_csv(file_path, encoding="ISO-8859-1")

        # Seçilen göstergeyi filtreliyoruz
        selected_indicator = "Completion rate, primary education, both sexes (%)"
        df_filtered = df[df["Series"] == selected_indicator]

        # Gereksiz sütunları kaldır ve yıllık verileri uzun formata çevir
        df_filtered = df_filtered.drop(columns=["Series", "Series Code"])
        df_filtered = df_filtered.melt(id_vars=["Country Name", "Country Code"],
                                       var_name="Year",
                                       value_name="Completion Rate")

        # Yıl sütununu temizleyelim ve tam tarih formatına çevirelim
        df_filtered["Year"] = df_filtered["Year"].str.extract("(\\d{4})").astype(int)
        df_filtered = df_filtered[df_filtered["Year"] <= 2020]  # 2020'ye kadar olan verileri alalım
        df_filtered["Year"] = pd.to_datetime(df_filtered["Year"].astype(str) + "-01-01")

        # Completion Rate sütunundaki eksik değerleri yönetelim
        df_filtered["Completion Rate"] = pd.to_numeric(df_filtered["Completion Rate"], errors="coerce")

        # Ülke bazında eksik veri yüzdesini hesaplayalım
        missing_percentage = df_filtered.groupby("Country Name")["Completion Rate"].apply(lambda x: x.isnull().mean())

        # %50'den fazla eksik verisi olan ülkeleri silelim
        countries_to_drop = missing_percentage[missing_percentage > 0.5].index
        df_filtered = df_filtered[~df_filtered["Country Name"].isin(countries_to_drop)]

        # Geri kalan eksik verileri ülke ortalamasıyla dolduralım
        df_filtered["Completion Rate"] = df_filtered.groupby("Country Name")["Completion Rate"].transform(
            lambda x: x.fillna(x.mean()))

        # Global analiz için tüm ülkelerin ortalamasını alalım
        df_global = df_filtered.groupby("Year")["Completion Rate"].mean().reset_index()

        # 2020'deki düşüşü düzeltmek için 2021 sonrası için bir toparlanma trendi ekleyelim
        df_global.loc[df_global["Year"] == pd.Timestamp("2020-01-01"), "Completion Rate"] = \
        df_global[df_global["Year"] < pd.Timestamp("2020-01-01")]["Completion Rate"].mean()

        # Prophet için veri çerçevesini uygun hale getirelim
        df_prophet = df_global.rename(columns={"Year": "ds", "Completion Rate": "y"})

        # Prophet modelini oluşturuyoruz
        model = Prophet(
            changepoint_prior_scale=0.08,  # Daha dengeli değişim noktası ayarı
            seasonality_mode="additive",  # Mevsimselliği daha dengeli hale getirmek için
            yearly_seasonality=True  # Yıllık trendi koruyalım
        )

        # Manuel değişim noktaları ekleyelim (Covid-19 etkisini azaltacak şekilde)
        model.add_seasonality(name='yearly', period=1, fourier_order=10)  # Yıllık etki ekleyelim
        model.changepoints = df_prophet[(df_prophet['ds'] >= '2005-01-01') & (df_prophet['ds'] <= '2020-01-01')]['ds']

        # Modeli eğitelim
        model.fit(df_prophet)

        # Gelecek 5 yıl için tahmin yapalım (2021-2025)
        future = model.make_future_dataframe(periods=5, freq='Y')
        future['cap'] = 100  # Tahminin üst sınırını belirleyelim
        future['floor'] = df_prophet['y'].min()
        forecast = model.predict(future)

        # Sonuçları görselleştirelim
        plt.figure(figsize=(12, 6))
        plt.plot(df_prophet["ds"], df_prophet["y"], label="Gerçek Değerler", marker="o", color="blue")
        plt.plot(forecast["ds"], forecast["yhat"], label="Tahmin (Prophet)", linestyle="dashed", marker="o",
                 color="red")
        plt.fill_between(forecast["ds"], forecast["yhat_lower"], forecast["yhat_upper"], alpha=0.1,
                         label="Güven Aralığı")
        plt.xlabel("Yıl")
        plt.ylabel("Tamamlama Oranı (%)")
        plt.title("Global Eğitim Tamamlama Oranı Tahmini (Prophet) (2021-2025)")
        plt.legend()
        plt.grid(True)
        plt.show()

    else:
        print("Geçersiz seçenek, lütfen tekrar deneyin.")



