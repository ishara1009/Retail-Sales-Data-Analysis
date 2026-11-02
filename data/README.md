# Dataset setup and attribution

This project uses the **Online Retail** dataset from the UCI Machine Learning
Repository. Each row is an invoice line, not necessarily a complete order.

- Official page: https://archive.ics.uci.edu/dataset/352/online+retail
- Creators/donors: Daqing Chen, Sai Liang Sain, and Kun Guo
- Expected file: `data/raw/Online Retail.xlsx`
- UCI dataset license shown on the official page: **CC BY 4.0**

Download the dataset from the official page, extract it if downloaded as an
archive, and place the original workbook at the expected path. The workbook is
ignored by Git and is never modified by the pipeline. Dataset attribution and
license remain separate from the MIT license used for this project's code.

Generated CSV files are written to `data/processed/` and are ignored by Git.

