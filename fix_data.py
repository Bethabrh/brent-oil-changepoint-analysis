import pandas as pd

df = pd.read_csv('data/DCOILBRENTEU.csv')
df.columns = ['Date', 'Price']
df = df[df['Price'] != '.']
df['Price'] = df['Price'].astype(float)
df['Date'] = pd.to_datetime(df['Date'])

# Trim to the assignment's exact date range
df = df[(df['Date'] >= '1987-05-20') & (df['Date'] <= '2022-09-30')]

# Save in the same day-month-yy string format as the original file
df_out = df.copy()
df_out['Date'] = df_out['Date'].dt.strftime('%d-%b-%y')
df_out.to_csv('data/BrentOilPrices.csv', index=False)

print(f'Rows: {len(df_out)}')
print(f'Date range: {df["Date"].min()} to {df["Date"].max()}')
print(df_out.head())
print(df_out.tail())