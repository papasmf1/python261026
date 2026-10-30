"""Clean and analyze the Korean birth statistics workbook with pandas."""

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd


WORKBOOK = Path(__file__).with_name("출생아수__합계출산율__자연증가_등.xlsx")
CLEANED_CSV = Path(__file__).with_name("birth_statistics_cleaned.csv")
CHART_PNG = Path(__file__).with_name("births_by_year.png")

METRICS = {
    "출생아수(명)": "Births",
    "자연증가건수(명)": "Natural increase",
    "조출생률(천명당)": "Crude birth rate",
    "자연증가율(천명당)": "Natural increase rate",
    "합계출산율(명)": "Total fertility rate",
    "출생성비(명)": "Sex ratio at birth",
}


def load_and_clean() -> pd.DataFrame:
    """Load the source wide table and return one cleaned row per year."""
    if not WORKBOOK.is_file():
        raise FileNotFoundError(f"Workbook not found: {WORKBOOK}")

    raw = pd.read_excel(WORKBOOK, sheet_name="데이터", index_col=0)
    raw = raw.dropna(axis=0, how="all").dropna(axis=1, how="all")
    raw.index = raw.index.astype(str).str.strip()
    raw.columns = raw.columns.astype(str).str.strip()

    if raw.index.has_duplicates:
        raise ValueError("Duplicate metric names found in the source workbook.")
    if raw.columns.has_duplicates:
        raise ValueError("Duplicate year columns found in the source workbook.")

    years = pd.to_numeric(pd.Index(raw.columns), errors="coerce")
    if years.isna().any() or (years % 1 != 0).any():
        raise ValueError("Year headers must all be valid integer years.")
    raw.columns = years.astype(int)

    numeric = raw.apply(pd.to_numeric, errors="coerce")
    invalid_values = raw.notna() & numeric.isna()
    if invalid_values.any().any():
        invalid_locations = [
            f"{raw.index[row]}, {raw.columns[column]}"
            for row, column in zip(*invalid_values.to_numpy().nonzero())
        ]
        raise ValueError(
            "Non-numeric source values found at metric/year: "
            + ", ".join(invalid_locations)
        )

    cleaned = numeric.T.rename_axis("Year").sort_index()
    cleaned.index = cleaned.index.astype(int)
    cleaned.columns.name = None

    missing_metrics = set(METRICS).difference(cleaned.columns)
    if missing_metrics:
        raise ValueError(f"Expected metrics are missing: {sorted(missing_metrics)}")
    if cleaned.index.has_duplicates:
        raise ValueError("Duplicate years found after cleaning.")

    missing_cells = int(cleaned.isna().sum().sum())
    print("데이터 정제 및 품질 점검")
    print(f"  관측 연도 수: {len(cleaned)}")
    print(f"  연도 범위: {cleaned.index.min()}-{cleaned.index.max()}")
    print(f"  결측 셀(대체하지 않고 유지): {missing_cells}")
    print(f"  중복 연도 행: {cleaned.index.duplicated().sum()}")
    print(f"  숫자가 아닌 원본 값: {int(invalid_values.sum().sum())}")
    return cleaned


def analyze(data: pd.DataFrame) -> None:
    births = data["출생아수(명)"]
    fertility = data["합계출산율(명)"]
    natural_increase = data["자연증가건수(명)"]

    print("\n기초 통계")
    print(data[list(METRICS)].describe().round(2).to_string())

    decades = data.assign(Decade=(data.index // 10) * 10).groupby("Decade").agg(
        Years=("출생아수(명)", "count"),
        Mean_births=("출생아수(명)", "mean"),
        Mean_total_fertility_rate=("합계출산율(명)", "mean"),
        Mean_natural_increase=("자연증가건수(명)", "mean"),
    )
    print("\n10년 단위 비교 (2020년대는 2020-2025년)")
    print(decades.round(2).to_string())

    yearly_change = pd.DataFrame(
        {
            "Births_change": births.diff(),
            "Births_change_pct": births.pct_change(fill_method=None) * 100,
        }
    ).dropna()
    print("\n전년 대비 출생아 수 증감 상위")
    print("증가 상위:")
    print(yearly_change.nlargest(5, "Births_change").round(2).to_string())
    print("감소 상위:")
    print(yearly_change.nsmallest(5, "Births_change").round(2).to_string())

    birth_peak_year = int(births.idxmax())
    birth_low_year = int(births.idxmin())
    fertility_peak_year = int(fertility.idxmax())
    fertility_low_year = int(fertility.idxmin())
    print("\n최고·최저 연도")
    print(
        f"Births: peak {birth_peak_year} ({births.max():,.0f}), "
        f"low {birth_low_year} ({births.min():,.0f})"
    )
    print(
        f"Total fertility rate: peak {fertility_peak_year} "
        f"({fertility.max():.3f}), low {fertility_low_year} "
        f"({fertility.min():.3f})"
    )

    correlation_data = data[
        ["출생아수(명)", "합계출산율(명)", "자연증가건수(명)", "출생성비(명)"]
    ]
    print("\n피어슨 상관계수")
    print(correlation_data.corr().round(3).to_string())

    negative_years = natural_increase[natural_increase < 0].index
    if len(negative_years):
        first_negative_year = int(negative_years.min())
        print(
            "\n자연증가건수가 처음 음수가 된 연도: "
            f"{first_negative_year}년 ({natural_increase.loc[first_negative_year]:,.0f}명)"
        )
    else:
        print("\n분석 기간 동안 자연증가건수는 음수가 아닙니다.")

    births_change_pct = (births.iloc[-1] / births.iloc[0] - 1) * 100
    fertility_change_pct = (fertility.iloc[-1] / fertility.iloc[0] - 1) * 100
    print(
        f"\n{data.index[0]}년 대비 {data.index[-1]}년: 출생아 수 "
        f"{births_change_pct:.1f}%, 합계출산율 {fertility_change_pct:.1f}% 변화"
    )


def save_births_chart(data: pd.DataFrame) -> None:
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        data.index,
        data["출생아수(명)"],
        color="#1769aa",
        linewidth=2,
        marker="o",
        markersize=3,
    )
    ax.set(
        title="대한민국 연도별 출생아 수 (1970–2025)",
        xlabel="연도",
        ylabel="출생아 수 (명)",
    )
    ax.grid(True, alpha=0.3)
    ax.ticklabel_format(axis="y", style="plain")
    fig.tight_layout()
    fig.savefig(CHART_PNG, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"\nChart saved: {CHART_PNG.name}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cleaned = load_and_clean()
    cleaned.to_csv(CLEANED_CSV, index_label="Year", encoding="utf-8-sig")
    print(f"Cleaned data saved: {CLEANED_CSV.name}")
    analyze(cleaned)
    save_births_chart(cleaned)


if __name__ == "__main__":
    main()
