from pathlib import Path
import pandas as pd
import numpy as np
import tempfile
COLS=['generation_kwh', 'load_kwh', 'export_kwh', 'import_kwh']
RATE='self_consumption_pct'
TOTALS={'generation_kwh': 201748.0, 'load_kwh': 214902.0, 'export_kwh': 29615.0, 'import_kwh': 42769.0}
METRIC_TOTALS={'self_consumed_kwh': 172133.0, 'balance_gap_kwh': 0.0}
def check_a(clean,audit):
    assert len(clean)==719
    assert pd.api.types.is_datetime64_any_dtype(clean.date)
    assert clean.date.min()==pd.Timestamp('2026-07-01') and clean.date.max()==pd.Timestamp('2026-08-29')
    assert not clean.duplicated(['date','entity_id']).any()
    assert not clean.isna().any().any()
    assert set(clean.entity_id)=={f'E{i:02d}' for i in range(1,13)}
    assert audit.loc[audit.action=='quarantined','source_row'].nunique()==4
    assert audit.loc[audit.action=='dropped_duplicate','source_row'].nunique()==3
    assert audit.source_row.between(2,727).all() and audit.reason.str.len().gt(0).all()
    for col,total in TOTALS.items():
        assert pd.api.types.is_numeric_dtype(clean[col])
        assert (clean[col]>=0).all() and abs(clean[col].sum()-total)<.001, col
    pd.testing.assert_frame_equal(clean.reset_index(drop=True),clean.sort_values(['date','entity_id']).reset_index(drop=True))
def check_b(detail,daily,entities):
    assert len(detail)==719 and len(daily)==60 and len(entities)==12
    assert daily.observed_rows.sum()==719
    expected=100*detail.rate_numerator/detail.rate_denominator.replace(0,np.nan)
    assert np.allclose(detail[RATE],expected,equal_nan=True)
    for table in [daily,entities]:
        assert np.allclose(table['weighted_'+RATE],100*table.rate_numerator/table.rate_denominator.replace(0,np.nan),equal_nan=True)
        for col,total in TOTALS.items(): assert abs(table[col].sum()-total)<.001,col
    assert abs(100*detail.rate_numerator.sum()/detail.rate_denominator.sum()-85.32079624085493)<1e-8
    assert daily.date.is_monotonic_increasing
    for col,total in METRIC_TOTALS.items():
        assert col in detail and abs(detail[col].sum()-total)<.001, col
def check_c(paths):
    assert len(paths)==4
    assert {p.name for p in paths}=={'01_trend.png','02_comparison.png','03_relationship.png','04_report.txt'}
    for p in paths:
        assert isinstance(p,Path) and p.is_file() and p.stat().st_size>100
        if p.suffix=='.png':assert p.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
        else:
            text=p.read_text(encoding='utf-8');assert '719' in text and '720' in text
def mini_b(fn,clean):
    small=clean.head(3).copy();before=small.copy(deep=True)
    d,day,entity=fn(small)
    pd.testing.assert_frame_equal(small,before)
    # A hand-checkable sample from the first three clean records.
    expected={'self_consumed_kwh': [355.0, 193.0, 417.0], 'balance_gap_kwh': [0.0, 0.0, 0.0]}
    if list(small.entity_id)==['E01','E02','E03'] and (small.date==pd.Timestamp('2026-07-01')).all():
        for col,values in expected.items(): assert np.allclose(d[col],np.array(values,dtype=float),equal_nan=True),col
    zero=small.copy();zero[COLS]=0
    d,day,entity=fn(zero)
    assert d[RATE].isna().all(), 'Zero denominator is undefined'
    assert day['weighted_'+RATE].isna().all()
    assert entity['weighted_'+RATE].isna().all()
def mini_a(fn):
    base=pd.read_csv(Path(__file__).parent/'02_data.csv',dtype=str,keep_default_na=False)
    base=base[(base.entity_id=='E02') & (base.date=='2026-07-10')].iloc[[0]].copy()
    base['entity_id']=' e02 ';base['segment']=''
    invalid=base.copy();invalid['date']='not-a-date'
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'mini.csv';pd.concat([base,base,invalid]).to_csv(path,index=False)
        clean,audit=fn(path)
    assert len(clean)==1 and clean.entity_id.iloc[0]=='E02' and clean.segment.iloc[0]=='North'
    assert audit.loc[audit.action=='quarantined','source_row'].nunique()==1
    assert audit.loc[audit.action=='dropped_duplicate','source_row'].nunique()==1
if __name__=='__main__':
    import importlib.util
    spec=importlib.util.spec_from_file_location('runner',Path(__file__).parent/'06_group_main.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    a=runner.load('07_student_A.py');b=runner.load('08_student_B.py')
    mini_a(a.load_and_clean)
    clean,audit=a.load_and_clean(Path(__file__).parent/'02_data.csv');check_a(clean,audit)
    mini_b(b.calculate_metrics,clean);check_b(*b.calculate_metrics(clean))
    runner.main();print('PASS: mini checks and integration')
