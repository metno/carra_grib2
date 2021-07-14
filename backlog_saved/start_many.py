import json
import find_parent

domains = ["NE","IGB"]
years = [ 1990 + i for i in range(2022-1990)]


k = 0
for domain in domains:
    for year in years:
        startDate = "%d0101" % year
        endDate = "%d1231" % year
        print(domain+str(year))
        args = {"json":"parent_exps.json","date":startDate,"enddate":endDate,"domain":domain}
        plan = find_parent.get_plan(args)
        for i in range(len(plan)):
            parent = list(plan[i].keys())[0]
            p = plan[i][parent]
            suiteName = "%s_%d_%d" % (domain,year,i)
            arg2 = {"date":p["startDate"],
                    "enddate":p["endDate"],
                    "suite":suiteName,
                    "parent":parent}
            k += 1
            print("Job args: ",k, arg2)

print(k," streams added (not really, just a dry run)")

