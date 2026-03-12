import plotly.express as px
import pandas as pd

# Liste tronquée des clusters (les 10 premiers + celui contenant MYO1D)
cluster_data = [
    ["ENSGALG00010003557", "ENSGALG00010003644", "ENSGALG00010003584", "ENSGALG00010003635", "ENSGALG00010003643",
     "ENSGALG00010003537", "ENSGALG00010003598", "ENSGALG00010003640", "ENSGALG00010003576", "ENSGALG00010003565",
     "ENSGALG00010003614", "ENSGALG00010003563", "ENSGALG00010003575", "ENSGALG00010003613", "ENSGALG00010003623",
     "ENSGALG00010003529"],
    ["ENSGALG00010018015", "LMCD1", "MERTK", "VNN2", "IGFBP2", "TOB2", "EHD3", "AARS2", "COL13A1", "STK11", "IDS",
     "CDK9", "SLC4A1", "APLP2"],
    ["PIAS3", "ADGRG1", "ENG", "SGSM3", "STAT5A", "WLS", "HSPG2", "GPR182", "TIE1", "CD34", "ARSG", "HIP1"],
    ["CYP4B7", "ACAD11", "ATIC", "HAO2", "ACOX1", "EHHADH", "FAM110B", "AQP11", "KYNU", "NCALD", "AASS", "FAXDC2"],
    ["ENSGALG00010001804", "MBP", "NRG2", "SH3GLB2", "ENSGALG00010006728", "SPPL3", "F7", "PIK3IP1", "AADAT",
     "ENSGALG00010000853"],
    ["HSPD1", "ORC6", "RARS", "ZNF622", "TCP1", "ACAD9", "HSPA9", "RCL1", "PSMG1", "FASTKD2"],
    ["ENSGALG00010023758", "CTIF", "MTSS2", "CD151", "SSPN", "SUFU", "TEAD3", "DENND6B", "DNAJB5", "UBE2D2"],
    ["FAM214A", "TRAK1", "CAPN5", "ENSGALG00010026220", "RAB43", "PAM", "ITIH2", "SORBS1", "PROS1",
     "ENSGALG00010004860"],
    ["KIAA1524", "ATAD2", "CKAP5", "POLA1", "KIAA1328", "MSH6", "GEN1", "MMS22L", "CIT", "DNA2"],
    ["ELAPOR2", "OSBPL5", "ABHD17B", "SOX6", "FBLN2", "PDE5A", "VIPR2", "IFT122", "GFRA1"],
    ["ENSGALG00010004705", "SLC29A3", "MYO1D", "CACNB1", "KDM5B"]
]

# Générer les données pour le sunburst
sunburst_data = []
highlight_clusters = set()
for i, genes in enumerate(cluster_data):
    cluster_label = f"Cluster {i+1}"
    for gene in genes:
        sunburst_data.append({"cluster": cluster_label, "gene": gene})
        if gene == "MYO1D":
            highlight_clusters.add(cluster_label)

df = pd.DataFrame(sunburst_data)
df["highlight"] = df["cluster"].apply(lambda c: "MYO1D cluster" if c in highlight_clusters else "Other")

# Créer le graphique sunburst avec un highlight complet du cluster contenant MYO1D
fig = px.sunburst(
    df,
    path=["highlight", "cluster", "gene"],
    color="highlight",
    color_discrete_map={"MYO1D cluster": "red", "Other": "lightblue"},
    title="Sunburst des gènes par cluster - Highlight du cluster contenant MYO1D"
)

fig.update_layout(margin=dict(t=40, l=0, r=0, b=0))

fig.show()
