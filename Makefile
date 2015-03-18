# This file is part of census2dbf.
# https://github.com/fitnr/census2dbf

# Licensed under the GPLv3 license:
# http://www.opensource.org/licenses/GPLv3-license
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>
readme.rst: readme.md
	pandoc $< -o $@