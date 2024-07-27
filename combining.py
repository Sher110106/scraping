import pandas as pd


first_df = pd.read_csv('designation_salaries14.csv')
second_df = pd.read_csv('mergee13_output.csv')

merged_df = pd.merge(second_df, first_df, on='Name', how='left', suffixes=('', '_new'))


for col in ['Role1', 'Role2', 'Role3', 'Role4', 'SalaryRole1', 'SalaryRole2', 'SalaryRole3', 'SalaryRole4']:
    merged_df[col] = merged_df[col + '_new'].combine_first(merged_df[col])
    merged_df.drop(columns=[col + '_new'], inplace=True)


merged_df.to_csv('mergee14_output.csv', index=False)

print("CSV files have been merged successfully!")
