import pandas as pd
import streamlit as st
import io
import calendar

st.set_page_config(page_title="Roster Converter", layout="centered")

st.title("📅 Roster Converter")
st.write("Upload file roster, pilih bulan & tahun, lalu download hasil konversi.")

# === Input bulan & tahun ===
col1, col2 = st.columns(2)
month = col1.number_input("Bulan", min_value=1, max_value=12, value=8)
year = col2.number_input("Tahun", min_value=2000, max_value=2100, value=2025)

sheetroster = 'ROSTER'
sheetkaryawan = 'KARYAWAN'
sheetmroster = 'MROSTER'

# === Upload file ===
uploaded_file = st.file_uploader("Upload roster_gs.xlsx", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Baca semua sheet
        df_roster = pd.read_excel(uploaded_file, sheet_name=sheetroster)
        df_map = pd.read_excel(uploaded_file, sheet_name=sheetkaryawan)
        df_mroster = pd.read_excel(uploaded_file, sheet_name=sheetmroster)

        # Siapkan kolom
        # day_columns = [str(i) for i in range(1, 32)]
        num_days = calendar.monthrange(year, month)[1]
        day_columns = [str(i) for i in range(1, num_days + 1)]
        df_roster.columns = df_roster.columns.map(lambda x: str(x) if isinstance(x, int) else x)

        # Reshape (melt)
        df_melted = df_roster.melt(id_vars=['NIK'], value_vars=day_columns,
                                   var_name='day', value_name='code_mroster')

        # Buat tanggal lengkap
        df_melted['day'] = df_melted['day'].astype(int)
        df_melted['tanggal_roster'] = pd.to_datetime({
            'year': year,
            'month': month,
            'day': df_melted['day']
        })

        # Merge data
        df_final = df_melted.merge(df_map, how='left', left_on='NIK', right_on='noinduk_karyawan')
        df_final = df_final.merge(df_mroster, how='left', left_on='code_mroster', right_on='code_mroster')

        # Pilih kolom akhir
        df_output = df_final[['id_karyawan', 'tanggal_roster', 'id_mroster']]
        df_output['tanggal_roster'] = df_output['tanggal_roster'].dt.strftime('%m/%d/%Y')

        # Siapkan untuk download
        buffer = io.BytesIO()
        df_output.to_excel(buffer, index=False)
        buffer.seek(0)

        st.success("✅ File berhasil dikonversi!")
        st.download_button(
            label="📥 Download Hasil",
            data=buffer,
            file_name=f'roster_converted_{year}_{month:02}.xlsx',
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Terjadi error: {e}")


