import pandas as pd
from scipy.stats import pearsonr

rozklad = pd.read_excel(r'Rozklad.xlsx')
pocasie = pd.read_excel(r'Stanice_Petrzalka.xlsx')

# Aggregate weather
pocasie.drop(['čas'], axis=1, inplace=True)

# Define specifical range function
range_f = lambda x: x.max() - x.min()
range_f.__name__ = 'range'

# First aggregation
pocasie_aggr = pocasie.groupby(by=['deň'], as_index=False).agg(['max', 'min', range_f, 'var', 'mean']).reset_index()

# Second aggregation
number_of_monthes = 7
pocasie_aggr['months_ticks'] = [i//30 + 1 if (i//30 + 1)!=8 else number_of_monthes for i in range(0,len(pocasie_aggr))] # Here is manual update of month
pocasie_aggr = pocasie_aggr.iloc[:,1:]
pocasie_aggr = pocasie_aggr.groupby(by=['months_ticks'], as_index=False).agg(['max', 'min', range_f, 'var', 'mean']).reset_index()

# Export for further analysis in power bi
pocasie_aggr.to_csv(r'aggregated_weather.csv', index=False, header=False)

# Few additional manipulations
list_of_cols = []
for i in pocasie_aggr.columns:
    list_of_cols.append('_'.join(i))

pocasie_aggr = pd.read_csv(r'aggregated_weather.csv', header=None)
pocasie_aggr.columns = list_of_cols
pocasie_aggr.rename({'months_ticks__':'Mesiac'}, axis=1, inplace=True)

# Create and export final dataframe
final_df = rozklad.merge(pocasie_aggr, on='Mesiac', how='left')
final_df.dropna(inplace=True)
final_df.to_excel(r'final_df.xlsx', index=False)

# Find correlations regardless of place
corr_full = final_df.iloc[:,4:].corr().iloc[:,:1]
corr_full.to_excel(r'corr_without_places.xlsx')

list_of_cols.pop(0)
list_of_corrs = []
list_of_vzorky = []
list_of_cols_for_df = []

for vzorka in final_df['Vzorky september'].unique():
    for col in list_of_cols:
        corr, _ = pearsonr(final_df['% rozkladu'][final_df['Vzorky september']==vzorka],final_df[col][final_df['Vzorky september']==vzorka])
        list_of_corrs.append(corr)
        list_of_vzorky.append(vzorka)
        list_of_cols_for_df.append(col)

df_1, df_1.columns = pd.DataFrame([list_of_vzorky, list_of_cols_for_df, list_of_corrs]).T, ['Vzorka', 'Hodnota', 'Person_corr']

# Export final correlations
df_1.to_excel(r'correlations_by_place.xlsx', index=False)