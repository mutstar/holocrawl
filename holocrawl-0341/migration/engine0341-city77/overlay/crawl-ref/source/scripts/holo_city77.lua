local arguments = crawl.script_args()
assert(arguments[1], "Supply the validation output directory")
assert(crawl.holo_city_test(arguments[1]))
