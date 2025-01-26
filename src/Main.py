import pandas as pd
import matplotlib.pyplot as plt

# Dosya yolunu belirt
file_path = r"C:\Users\Lenovo\Desktop\PythonProject2\src\NetAttendence.xlsx"  # Dosya yolunu kontrol edin
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

# `Unnamed` sütunlarını kaldır
unnamed_cols = [col for col in data.columns if "Unnamed" in str(col)]
data.drop(columns=unnamed_cols, inplace=True)

# Sütun adlarını kontrol et
print("Sütunlar:", data.columns)

# Gerekli sütunları yeniden adlandır
data.rename(columns={
    "Country": "Country",
    "Region": "Region",
    "EducationLevel": "Education Level",
    "Total": "Value",  # Eğitime katılım oranı bu sütundaysa
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
data["Value"] = pd.to_numeric(data["Value"], errors="coerce")  # Metin değerleri NaN olur
data.dropna(subset=["Value"], inplace=True)  # NaN değerleri kaldır


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
mean_values = data.groupby(["Region", "Education Level"])["Value"].mean().unstack()

print("Veri setindeki gerekli sütunlar:", data.columns[:5])

# Grafik çizimi
mean_values.plot(kind="bar", figsize=(12, 8), edgecolor="black")
plt.title("Kıtalar Bazında Eğitime Katılım Oranları (Ortalama)")


plt.xlabel("Kıtalar")
plt.ylabel("Katılım Oranı (%)")
plt.legend(title="Eğitim Seviyesi", loc="upper right")
plt.tight_layout()
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()

total_values = data.groupby("Region")["Value"].mean()
total_values.plot(kind="pie", autopct="%1.1f%%", startangle=90, figsize=(8, 8), colormap="viridis")
plt.title("Kıtalar Bazında Eğitime Katılım Oranları Dağılımı")
plt.ylabel("")
plt.show()

region_countries = data.groupby("Region")["Country"].unique()
for region, countries in region_countries.items():
    print(f"{region} bölgesindeki ülkeler:")
    print(", ".join(countries))
    print("\n")

specific_region = "ECA"
region_data = data[data["Region"] == specific_region]
print(region_data.groupby("Country")[["Education Level", "Value"]].mean())

for region in desired_regions:
    region_data = data[data["Region"] == region]

    if region_data.empty:
        print(f"{region} bölgesi için veri bulunamadı.")
        continue

    for region in desired_regions:
        region_data = data[data["Region"] == region]

        if region_data.empty:
            print(f"{region} bölgesi için veri bulunamadı.")
            continue

        for region in desired_regions:
            region_data = data[data["Region"] == region]

            if region_data.empty:
                print(f"{region} bölgesi için veri bulunamadı.")
                continue

            # Ülkelere göre analiz
            mean_values = region_data.groupby("Country")["Value"].mean()


            mean_values.plot(kind="bar", figsize=(14, 7), color="coral", edgecolor="black")
            plt.title(f"{region} Bölgesindeki Ülkelerin Katılım Oranı", fontsize=16)
            plt.xlabel("Ülkeler", fontsize=12)
            plt.ylabel("Katılım Oranı (%)", fontsize=12)
            plt.xticks(rotation=45, ha="right", fontsize=10)
            plt.tight_layout()
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.show()

            # Kullanıcıdan giriş bekle
            input(f"{region} bölgesi için grafiği incelediniz mi? Devam etmek için Enter'a basın.")








