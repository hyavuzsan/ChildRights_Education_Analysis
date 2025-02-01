import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
import sys
import logging
import warnings
import seaborn as sns

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


sys.stderr = open('nul', 'w')

# CmdStanpy ve Prophet uyarılarını kapatıyoruz
logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
logging.getLogger("prophet").setLevel(logging.ERROR)

# FutureWarning mesajlarını kapatıyoruz
warnings.simplefilter(action='ignore', category=FutureWarning)


file_path = r"C:\Users\Lenovo\Desktop\Project\src\NetAttendence.xlsx"
sheets = ["One year before", "Primary", "Lower secondary", "Upper secondary"]

# Tüm sekmeleri birleştiriyoruz
data_frames = []
for sheet in sheets:
    df = pd.read_excel(file_path, sheet_name=sheet)
    df["Education Level"] = sheet  # Sekme adını bir sütun olarak ekle
    data_frames.append(df)

# Verileri birleştiriyoruz
data = pd.concat(data_frames, ignore_index=True)


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

# Gerekli sütunları seçiyoruz
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

# bölgeleri filtreliyoruz
desired_regions = list(region_mapping.values())
data = data[data["Region"].isin(desired_regions)]

# Kıtalar bazında çubuk grafik için veri hazırlığı
mean_values = data.groupby(["Region", "Education Level"])['Value'].mean().unstack()


while True:
    print("Hangi grafiği incelemek istiyorsunuz?")
    print("1) Kıtalar Bazında Eğitime Katılım Oranları (Ortalama)")
    print("2) Kıtalar Bazında Eğitime Katılım Oranları Dağılımı")
    print("3) Kıtalar Bazında İnternete Erişim Grafiği")
    for i, region in enumerate(desired_regions, start=4):
        print(f"{i}) {region} bölgesindeki ülkelerin eğitime katılım oranı")
    print("10) Dünya genelinde tahmini ilkokul bitirme oranlarını göster")
    print("11)Kümeleme sonuçlarının incelenmesi")
    choice = input("Lütfen bir seçenek girin (Çıkış için 'q'): ")


    if choice.lower() == 'q':
        break
    elif choice == "1":
        # Kıtalar bazında eğitime katılım oranlarını gruplandırıyoruz ve eğitim seviyelerine göre dağıtıyoruz
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
        plt.title("Kıtalar Bazında Eğitime Katılım Oranları Dağılımı (pasta dilimi) ")
        plt.ylabel("")
        plt.show()

    elif choice == "3":

        file_path = r"C:\Users\Lenovo\Desktop\Project\src\DigitalConnectivity.xlsx"
        sheet_name = "Upper Secondary"

        # Veriyi okuyoruz
        data = pd.read_excel(file_path, sheet_name=sheet_name)

        print("Sütunlar:", data.columns)

        #  Sütunları yeniden adlandırıyoruz
        data.rename(columns={
            "Countries and areas": "Country",
            "Region": "Region",
            "Total": "Value",
        }, inplace=True)

        data = data.drop(columns=[col for col in data.columns if "Unnamed" in col])

        # Value sütununu işliyoruz
        data["Value"] = pd.to_numeric(data["Value"].astype(str).str.replace('%', ''), errors="coerce")

        # Eksik değerleri kaldırıyoruz
        data.dropna(subset=["Value"], inplace=True)

        # Bölge isimlerini Türkçe olarak yazdırıyoruz
        region_mapping = {
            "SSA": "Sahra Altı Afrika",
            "LAC": "Latin Amerika ve Karayipler",
            "ECA": "Avrupa ve Orta Asya",
            "SA": "Güney Asya",
            "EAP": "Doğu Asya ve Pasifik",
            "MENA": "Orta Doğu ve Kuzey Afrika"
        }

        data["Region"] = data["Region"].map(region_mapping)

        # Kutu grafiği oluşturuyoruz
        plt.figure(figsize=(12, 8))
        sns.boxplot(data=data, x="Region", y="Value", hue="Region", palette="Set2", legend=False)
        plt.title("Bölgelere Göre Çocukların İnternete Erişim Oranı", fontsize=14)
        plt.xlabel("Bölgeler", fontsize=12)
        plt.ylabel("İnternete Erişim Oranı (%)", fontsize=12)
        plt.xticks(rotation=45, fontsize=10)
        plt.tight_layout()
        plt.show()

    elif choice.isdigit() and 4 <= int(choice) <= 3 + len(desired_regions):
        region_index = int(choice) - 4
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

            # Ülkeleri kıtalardan ayırıyoruz
            filtered_data = region_data[~region_data["Country"].isin(continent_names)]

            # Ülkeler bazında ortalamayı hesaplıyoruz
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

    elif choice == "10":

        # CmdStanpy ve FutureWarning mesajlarını kapat
        logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
        warnings.simplefilter(action='ignore', category=FutureWarning)

        file_path = r"C:\Users\Lenovo\Desktop\Project\src\Data.csv"

        df = pd.read_csv(file_path, encoding="ISO-8859-1")

        # Seçilen göstergeyi filtreliyoruz
        selected_indicator = "Completion rate, primary education, both sexes (%)"
        df_filtered = df[df["Series"] == selected_indicator]

        # Gereksiz sütunları kaldırıyoruz ve yıllık verileri uzun formata çevir
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
            changepoint_prior_scale=0.08,
            seasonality_mode="additive",
            yearly_seasonality=True
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

        # Görselleştirme
        plt.figure(figsize=(12, 6))
        plt.plot(df_prophet["ds"], df_prophet["y"], label="Gerçek Değerler", marker="o", color="blue")
        plt.plot(forecast["ds"], forecast["yhat"], label="Tahmin (Prophet)", linestyle="dashed", marker="o",
                 color="red")
        plt.fill_between(forecast["ds"], forecast["yhat_lower"], forecast["yhat_upper"], alpha=0.1,
                         label="Güven Aralığı")
        plt.xlabel("Yıl")
        plt.ylabel("Tamamlama Oranı (%)")
        plt.title("Global İlköğretim Tamamlama Oranı Tahmini (Prophet) (2021-2025)")
        plt.legend()
        plt.grid(True)
        plt.show()

    elif choice == "11":


        df = pd.read_csv(r"C:\Users\Lenovo\Desktop\Project\src\share-of-the-world-population-with-at-least-basic-education.csv")

        #Gerekli Sütunları Seçme ve Temizlik
        df = df.rename(columns={"Entity": "Country", "Year": "Year",
                                "Share of population with no formal education, 1820-2020": "No_Education_Share"})
        df = df[df["Year"] == 2020]  # Sadece 2020 yılı verisini al

        df = df[["Country", "Year", "No_Education_Share"]].dropna()

        #K-Means ile Kümeleme
        X = df[["No_Education_Share"]].values
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df["Cluster"] = kmeans.fit_predict(X)

        #Kümeleme Sonuçlarını Kaydet
        df.to_csv("clustering_results.csv", index=False)

        #Küme 1 İçindeki Ülkeleri Seçelim
        df_cluster_1 = df[df["Cluster"] == 1].copy()

        #Küme 1'i Yeni K-Means ile 4 Alt Kümeye Bölmek
        X_sub = df_cluster_1[["No_Education_Share"]].values
        kmeans_sub = KMeans(n_clusters=4, random_state=42, n_init=10)
        df_cluster_1["Sub_Cluster"] = kmeans_sub.fit_predict(X_sub)

        #Yeni Kümeleme Sonuçlarını Kaydet
        df_cluster_1.to_csv("cluster_1_subgroups.csv", index=False)

        # Genel Nokta Grafiği
        plt.figure(figsize=(14, 8))
        sns.stripplot(x="Cluster", y="No_Education_Share", data=df, hue="Cluster", jitter=True, palette="Set1",
                      alpha=0.7,
                      legend=False)
        plt.xlabel("Küme")
        plt.ylabel("No Education Share (%)")
        plt.title("Genel Eğitim Durumu Nokta Grafiği")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.show()

        # Tüm Küme Verilerini Kapsayan Kutu Grafiği
        plt.figure(figsize=(14, 8))
        sns.boxplot(x="Cluster", y="No_Education_Share", data=df, hue="Cluster", palette="Set2", legend=False)
        plt.xlabel("Küme")
        plt.ylabel("No Education Share (%)")
        plt.title("Tüm Kümelerin Eğitim Durumu Dağılımı")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.show()

        # Kümelerin Büyüklüğünü Gösteren Grafik
        plt.figure(figsize=(10, 6))
        sns.countplot(x="Cluster", data=df, hue="Cluster", palette="pastel", legend=False)
        plt.xlabel("Küme")
        plt.ylabel("Ülke Sayısı")
        plt.title("Her Kümedeki Ülke Sayısı")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.show()

        #Alt Küme Grafiklerini Tek Tek Gösterelim
        for sub_cluster in df_cluster_1["Sub_Cluster"].unique():
            df_sub = df_cluster_1[df_cluster_1["Sub_Cluster"] == sub_cluster].sort_values(by="No_Education_Share",
                                                                                          ascending=False)

            plt.figure(figsize=(18, 12))
            sns.barplot(y="Country", x="No_Education_Share", data=df_sub, hue="Country", palette="coolwarm",
                        legend=False)
            plt.xlabel("No Education Share (%)", fontsize=14)
            plt.ylabel("Ülke", fontsize=14)
            plt.title(f"Küme 1 - Alt Küme {sub_cluster} İçin Eğitim Durumu", fontsize=16)
            plt.grid(axis="x", linestyle="--", alpha=0.7)
            plt.xticks(rotation=45, fontsize=12)
            plt.yticks(fontsize=12)
            plt.tight_layout()
            plt.show()

        #Küme 0 ve Küme 2'nin Görselleştirilmesi
        for cluster in [0, 2]:
            df_cluster = df[df["Cluster"] == cluster].sort_values(by="No_Education_Share", ascending=False)

            plt.figure(figsize=(14, 8))
            sns.barplot(y="Country", x="No_Education_Share", data=df_cluster, hue="Country", palette="viridis",
                        legend=False)
            plt.xlabel("No Education Share (%)")
            plt.ylabel("Ülke")
            plt.title(f"Küme {cluster} İçin Eğitim Durumu")
            plt.grid(axis="x", linestyle="--", alpha=0.7)
            plt.xticks(rotation=45)
            plt.yticks(fontsize=10)
            plt.show()

        #Model Değerlendirme (Silhouette Score)
        silhouette_avg = silhouette_score(X, df["Cluster"])
        print(f"Silhouette Score: {silhouette_avg:.4f}")

        print("Kümeleme modeli başarıyla oluşturuldu ve analiz tamamlandı.")

    else:
        print("Geçersiz seçenek, lütfen tekrar deneyin.")

