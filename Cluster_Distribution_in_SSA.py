{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyPauRsUC2o7WudWtjuCGbgq",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/danielpazrosseboe/MasterDRC/blob/main/Cluster_Distribution_in_SSA.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "8gMGxp-0FY9P"
      },
      "outputs": [],
      "source": [
        "# Robust Africa map for clusters_yeh_spec.csv (handles various Natural Earth schemas)\n",
        "import os, io, zipfile, requests\n",
        "import pandas as pd\n",
        "import geopandas as gpd\n",
        "import matplotlib.pyplot as plt\n",
        "from pathlib import Path\n",
        "\n",
        "CLUST_PATH = \"/content/drive/My Drive/Master_Thesis/Surveys/clusters_yeh_spec.csv\"\n",
        "OUT_PATH   = \"/content/drive/My Drive/Master_Thesis/Surveys/africa_clusters.png\"\n",
        "\n",
        "# 1) Load clusters\n",
        "cl = pd.read_csv(CLUST_PATH, usecols=[\"country\",\"year\",\"cluster\",\"lat\",\"lon\"])\n",
        "cl[\"lat\"] = pd.to_numeric(cl[\"lat\"], errors=\"coerce\")\n",
        "cl[\"lon\"] = pd.to_numeric(cl[\"lon\"], errors=\"coerce\")\n",
        "cl = cl.dropna(subset=[\"lat\",\"lon\"])\n",
        "\n",
        "gdf = gpd.GeoDataFrame(\n",
        "    cl,\n",
        "    geometry=gpd.points_from_xy(cl[\"lon\"], cl[\"lat\"]),\n",
        "    crs=\"EPSG:4326\"\n",
        ")\n",
        "\n",
        "# 2) Ensure Natural Earth admin0 is available (via GitHub mirror)\n",
        "zip_url = \"https://github.com/nvkelso/natural-earth-vector/archive/refs/heads/master.zip\"\n",
        "local_zip = \"/content/ne_data.zip\"\n",
        "extract_dir = \"/content/ne_data\"\n",
        "\n",
        "if not os.path.exists(extract_dir):\n",
        "    print(\"Downloading Natural Earth shapefile from GitHub...\")\n",
        "    r = requests.get(zip_url, timeout=60)\n",
        "    r.raise_for_status()\n",
        "    with open(local_zip, \"wb\") as f:\n",
        "        f.write(r.content)\n",
        "    with zipfile.ZipFile(local_zip, \"r\") as z:\n",
        "        z.extractall(extract_dir)\n",
        "\n",
        "# Find the admin_0 countries shapefile\n",
        "shp_path = None\n",
        "for root, _, files in os.walk(extract_dir):\n",
        "    if \"ne_110m_admin_0_countries.shp\" in files:\n",
        "        shp_path = os.path.join(root, \"ne_110m_admin_0_countries.shp\")\n",
        "        break\n",
        "if shp_path is None:\n",
        "    raise FileNotFoundError(\"ne_110m_admin_0_countries.shp not found in Natural Earth archive.\")\n",
        "\n",
        "world = gpd.read_file(shp_path)\n",
        "\n",
        "# 3) Select Africa robustly\n",
        "africa = None\n",
        "for col in [\"CONTINENT\", \"continent\", \"CONTINENT_A\", \"CONTINENT_LC\", \"CONTINEN\"]:\n",
        "    if col in world.columns:\n",
        "        africa = world[world[col].astype(str).str.contains(\"Africa\", case=False, na=False)]\n",
        "        break\n",
        "\n",
        "if africa is None:\n",
        "    for col in [\"REGION_UN\", \"region_un\", \"REGION_WB\"]:\n",
        "        if col in world.columns:\n",
        "            africa = world[world[col].astype(str).str.contains(\"Africa\", case=False, na=False)]\n",
        "            break\n",
        "\n",
        "# Final fallback: spatial bounding box over Africa\n",
        "if africa is None or africa.empty:\n",
        "    # lon: -25..60, lat: -40..40 (rough Africa box)\n",
        "    africa = world.cx[-25:60, -40:40]\n",
        "\n",
        "# 4) Plot\n",
        "fig, ax = plt.subplots(figsize=(10, 10))\n",
        "africa.boundary.plot(ax=ax, linewidth=0.5)\n",
        "gdf.plot(ax=ax, markersize=0.08, alpha=0.6)  # default colors per notebook policy\n",
        "ax.set_title(\"DHS Cluster Distribution over Africa\", fontsize=14)\n",
        "ax.set_xlabel(\"Longitude\", fontsize = 12)\n",
        "ax.set_ylabel(\"Latitude\", fontsize = 12)\n",
        "ax.set_aspect(\"equal\", adjustable=\"box\")\n",
        "plt.tight_layout()\n",
        "\n",
        "Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)\n",
        "plt.savefig(OUT_PATH, dpi=220, bbox_inches=\"tight\")\n",
        "print(f\"Map saved → {OUT_PATH}\")\n"
      ]
    }
  ]
}