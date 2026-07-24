import os
import re
import sys
import pandas as pd
import matplotlib.pyplot as plt


FILE = os.path.join(os.path.dirname(__file__), '출생아수__합계출산율__자연증가_등_20260724153626.xlsx')
OUT_DIR = os.path.join(os.path.dirname(__file__), 'analysis_outputs')
os.makedirs(OUT_DIR, exist_ok=True)


def find_column(cols, keywords):
    for c in cols:
        low = str(c)
        for k in keywords:
            if k in low:
                return c
    return None


def clean_number_series(s):
    return pd.to_numeric(
        s.astype(str)
        .str.replace('\u2013', '')
        .str.replace('\u2014', '')
        .str.replace(',', '')
        .str.replace(' ', '')
        .str.replace('-', '')
        .str.replace('?', '')
        .str.strip(),
        errors='coerce')


def main():
    print('Reading', FILE)
    try:
        df = pd.read_excel(FILE, engine='openpyxl')
    except Exception as e:
        print('Failed to read Excel:', e)
        sys.exit(1)

    # Normalize column names
    df.columns = [str(c).strip() for c in df.columns]

    # Detect if file is wide-format (years in columns)
    year_like = [c for c in df.columns if re.search(r'\d{4}', str(c))]
    if len(year_like) > 3 and not any(k in str(df.columns[0]).lower() for k in ['year', '연도', '년도']):
        # Wide format: first column contains the variable name (예: 출생아수, 합계출산율)
        var_col = df.columns[0]
        # Melt
        df_long = df.melt(id_vars=[var_col], value_vars=year_like, var_name='year_raw', value_name='value')
        df_long['year'] = df_long['year_raw'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
        df_long['value_num'] = clean_number_series(df_long['value'])

        births_rows = df_long[df_long[var_col].astype(str).str.contains('출생|신생', na=False)]
        tfr_rows = df_long[df_long[var_col].astype(str).str.contains('합계출산율|출산율|tfr', na=False)]

        births_by_year = births_rows.groupby('year')['value_num'].sum(min_count=1).sort_index()
        tfr_by_year = None
        if not tfr_rows.empty:
            tfr_by_year = tfr_rows.groupby('year')['value_num'].mean().sort_index()

        cleaned = pd.DataFrame({'year': births_by_year.index, 'births_clean': births_by_year.values})
        if tfr_by_year is not None:
            cleaned = cleaned.set_index('year').join(tfr_by_year.rename('tfr')).reset_index()

        cleaned.to_csv(os.path.join(OUT_DIR, 'cleaned_births.csv'), index=False, encoding='utf-8-sig')

        # stats
        stats = cleaned.set_index('year').agg({'births_clean': ['sum', 'mean', 'median', 'count'], 'tfr': 'mean'})
        stats.columns = ['_'.join(map(str,c)).strip() for c in stats.columns]
        stats.to_csv(os.path.join(OUT_DIR, 'yearly_stats.csv'), encoding='utf-8-sig')

        # summary
        with open(os.path.join(OUT_DIR, 'summary.txt'), 'w', encoding='utf-8') as f:
            f.write('Original columns:\n')
            for c in df.columns:
                f.write(f'- {c}\n')
            f.write('\nDetected wide-format with variable column: %s\n' % var_col)
            f.write('Years covered: %s\n' % (', '.join(map(str, births_by_year.index.tolist()))))
            f.write('\nTop 5 year totals:\n')
            for yr, val in births_by_year.sort_values(ascending=False).head(5).items():
                f.write(f'{yr}: {int(val) if pd.notna(val) else "NA"}\n')

        # plot
        plt.figure(figsize=(10, 6))
        plt.plot(births_by_year.index, births_by_year.values, marker='o', linestyle='-')
        plt.xlabel('Year')
        plt.ylabel('출생아수')
        plt.title('연도별 출생아수')
        plt.grid(True)
        plt.tight_layout()
        plot_path = os.path.join(OUT_DIR, 'births_by_year.png')
        plt.savefig(plot_path)
        plt.close()

        print('분석 완료 (wide-format). 결과 저장:')
        print(' - cleaned CSV:', os.path.join(OUT_DIR, 'cleaned_births.csv'))
        print(' - yearly stats:', os.path.join(OUT_DIR, 'yearly_stats.csv'))
        print(' - summary:', os.path.join(OUT_DIR, 'summary.txt'))
        print(' - plot:', plot_path)
        return

    # --- Fall back to long-format handling (original code) ---
    # Detect year column
    year_col = find_column([c.lower() for c in df.columns], ['연도', '년도', 'year'])
    if year_col is not None:
        # map back to actual column name (case sensitive)
        for c in df.columns:
            if year_col == c.lower():
                year_col = c
                break

    if year_col is None:
        # fallback: first column
        year_col = df.columns[0]

    # Extract 4-digit year
    df['__year_tmp'] = df[year_col].astype(str).str.extract(r'(\d{4})')[0]
    df = df.dropna(subset=['__year_tmp']).copy()
    df['year'] = df['__year_tmp'].astype(int)
    df.drop(columns=['__year_tmp'], inplace=True)

    # Detect birth count column
    birth_col = find_column([c.lower() for c in df.columns], ['출생아', '출생', '신생아', '출생아수', '출생아수(명)'])
    if birth_col is not None:
        for c in df.columns:
            if birth_col == c.lower():
                birth_col = c
                break
    else:
        # try any numeric-like column other than year
        candidates = [c for c in df.columns if c != year_col]
        birth_col = None
        for c in candidates:
            s = clean_number_series(df[c])
            if s.notna().sum() > 0:
                birth_col = c
                break

    if birth_col is None:
        print('출생아수 칼럼을 찾을 수 없습니다. 컬럼 목록:', df.columns.tolist())
        sys.exit(1)

    # Clean births
    df['births_clean'] = clean_number_series(df[birth_col])

    # If 합계출산율 column present
    tfr_col = find_column([c.lower() for c in df.columns], ['합계출산율', 'tfr', '출산율'])
    if tfr_col is not None:
        for c in df.columns:
            if tfr_col == c.lower():
                tfr_col = c
                break
        df['tfr'] = clean_number_series(df[tfr_col])
    else:
        df['tfr'] = pd.NA

    # Keep relevant
    cleaned = df[['year'] + [birth_col] if birth_col not in ['year'] else ['year']].copy()
    cleaned['births_clean'] = df['births_clean']
    if 'tfr' in df.columns:
        cleaned['tfr'] = df.get('tfr')

    cleaned.to_csv(os.path.join(OUT_DIR, 'cleaned_births.csv'), index=False, encoding='utf-8-sig')

    # Aggregate births per year
    births_by_year = df.groupby('year')['births_clean'].sum(min_count=1).sort_index()

    # Basic stats
    stats = df.groupby('year').agg({ 'births_clean': ['sum', 'mean', 'median', 'count'], 'tfr': 'mean' })
    stats.columns = ['_'.join(map(str,c)).strip() for c in stats.columns]
    stats.to_csv(os.path.join(OUT_DIR, 'yearly_stats.csv'), encoding='utf-8-sig')

    # Save a short textual summary
    with open(os.path.join(OUT_DIR, 'summary.txt'), 'w', encoding='utf-8') as f:
        f.write('Original columns:\n')
        for c in df.columns:
            f.write(f'- {c}\n')
        f.write('\nDetected year column: %s\n' % year_col)
        f.write('Detected births column: %s\n' % birth_col)
        f.write('\nYears covered: %s\n' % (', '.join(map(str, births_by_year.index.tolist()))))
        f.write('\nTop 5 year totals:\n')
        for yr, val in births_by_year.sort_values(ascending=False).head(5).items():
            f.write(f'{yr}: {int(val) if pd.notna(val) else "NA"}\n')

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(births_by_year.index, births_by_year.values, marker='o', linestyle='-')
    plt.xlabel('Year')
    plt.ylabel('출생아수')
    plt.title('연도별 출생아수')
    plt.grid(True)
    plt.tight_layout()
    plot_path = os.path.join(OUT_DIR, 'births_by_year.png')
    plt.savefig(plot_path)
    plt.close()

    print('분석 완료. 결과 저장:')
    print(' - cleaned CSV:', os.path.join(OUT_DIR, 'cleaned_births.csv'))
    print(' - yearly stats:', os.path.join(OUT_DIR, 'yearly_stats.csv'))
    print(' - summary:', os.path.join(OUT_DIR, 'summary.txt'))
    print(' - plot:', plot_path)


if __name__ == '__main__':
    main()
