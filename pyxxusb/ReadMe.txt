

# Requirements:
- SWIG software (version 4)
- Python 32bit (Python 3.9 32bit)

# Coversion commands:
swig -c++ -python pyxxusb.i
python setup.py build_ext --inplace