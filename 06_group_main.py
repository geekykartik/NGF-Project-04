from pathlib import Path
import importlib.util
import sys
ROOT=Path(__file__).resolve().parent
def load(filename):
    spec=importlib.util.spec_from_file_location(Path(filename).stem,ROOT/filename)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def main():
    a=load('07_student_A.py');b=load('08_student_B.py');c=load('09_student_C.py');tests=load('11_checks.py')
    clean,audit=a.load_and_clean(ROOT/'02_data.csv');tests.check_a(clean,audit)
    detail,daily,entities=b.calculate_metrics(clean);tests.check_b(detail,daily,entities)
    out=ROOT/'results';out.mkdir(exist_ok=True)
    for name,table in [('clean',clean),('audit',audit),('detail',detail),('daily',daily),('entities',entities)]:
        table.to_csv(out/(name+'.csv'),index=False)
    tests.check_c(c.create_report(detail,daily,entities,out))
    print('PASS: outputs saved to',out)
if __name__=='__main__':
    try:main()
    except NotImplementedError as exc:
        print('PROJECT INCOMPLETE:',exc);sys.exit(2)
