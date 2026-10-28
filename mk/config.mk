LOCALE_DISABLE_POOTLE_DOWNLOAD=1

TEST_TARGETS += ipv6_ppp_tests

.PHONY: ipv6_ppp_tests
ipv6_ppp_tests:
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
