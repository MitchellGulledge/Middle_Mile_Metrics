import requests
import json
import meraki
from numpy import mean
import numpy
import matplotlib.pyplot as plt
import arrow
from operator import add 

# Author Mitchell Gulledge

# creating class to create all Meraki config
class MerakiConfig:

    # Defining your API key as a variable in source code is not recommended
    meraki_api_key = ''

    # authenticating to the Meraki SDK 
    meraki_dashboard = meraki.DashboardAPI(meraki_api_key)

    # creating header to authenticate API calls that do not have SDK yet
    meraki_request_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": meraki_api_key
    }

    # inputting org name to later map to Meraki org id
    meraki_org_name = 'Cloud Test Org'

    # creating variables for branch sites names
    site_1_branch_name = 'MMO_SF_Branch_Site'
    site_2_branch_name = 'MMO_Lon_Branch_Site'

    # creating variables for regional Hubs names
    site_1_hub_name = 'MMO_LAX_SIGraki_vMX'
    site_2_hub_name = 'MMO_LON_SIGraki_vMX'

    # creating variable for Meraki tag to filter how many networks we receive from the Meraki API
    meraki_tag = 'MMO'

    # utilizing SDK to fetch all organizations
    meraki_organizations = meraki_dashboard.organizations.getOrganizations()

    # iterating through the list of organizations and 
    # creating a match condition to set the org ID to the matching 'name' variable
    for orgs in meraki_organizations:

        if orgs['name'] == meraki_org_name:

            # setting meraki_org_id variable to orgs['id'] and 
            # since its in the MerakiConfig class we can reuse it whenever
            meraki_org_id = orgs['id']


    # utilizing sdk to fetch all networks in org with MMO tag
    meraki_organization_networks = meraki_dashboard.organizations.getOrganizationNetworks(
        meraki_org_id, total_pages='all', tags=[meraki_tag]
        )

    # iterating through list of networks from the Meraki API in the meraki_organization_networks
    # variable and setting if else statements to match network ID to network name in Meraki dashboard
    for networks in meraki_organization_networks:

        # setting conditional statements to match network naems to network IDs
        if networks['name'] == site_1_branch_name:

            # creating site 1 network id variable and setting it to networks['id']
            site_1_branch_id = networks['id']

        # setting conditional statements to match network naems to network IDs
        elif networks['name'] == site_2_branch_name:

            # creating site 2 network id variable and setting it to networks['id']
            site_2_branch_id = networks['id']

        # setting conditional statements to match network naems to network IDs
        elif networks['name'] == site_1_hub_name:

            # creating site 1 hub id variable and setting it to networks['id']
            site_1_hub_id = networks['id']

        # setting conditional statements to match network naems to network IDs
        elif networks['name'] == site_2_hub_name:

            # creating site 2 hub id variable and setting it to networks['id']
            site_2_hub_id = networks['id']

    # crafting URL to obtain all uplink statuses for devices in our Meraki organization
    meraki_uplink_status_url = "https://api.meraki.com/api/v1/organizations/" \
        + meraki_org_id + "/uplinks/statuses"

    # crafting payload for obtaining the uplink status for Meraki devices in our Meraki organization
    meraki_uplink_status_payload = None

    # performing request to obtain all uplink statuses for all devices in our Meraki dashboard
    meraki_uplink_status_response = requests.request(
        'GET', 
        meraki_uplink_status_url, 
        headers=meraki_request_headers, 
        data = meraki_uplink_status_payload
        )

    # converting meraki_uplink_status_response to json format
    meraki_uplink_status_json = json.loads(meraki_uplink_status_response.text.encode('utf8'))

    # iterating through uplink statuses to grab public IP for branch and Hub sites
    for uplinks in meraki_uplink_status_json:
        
        # setting conditional statement to match on network IDs for each branch and Hub
        if site_1_branch_id == uplinks['networkId']:

            # creating variable for branch IP and setting public IP to that
            site_1_branch_ip = uplinks['uplinks'][0]['publicIp']

            # creating variable for branch serial
            site_1_branch_serial = uplinks['serial']

        elif site_2_branch_id == uplinks['networkId']:

            # creating variable for branch IP and setting public IP to that
            site_2_branch_ip = uplinks['uplinks'][0]['publicIp']

            # creating variable for branch serial
            site_2_branch_serial = uplinks['serial']

        elif site_1_hub_id == uplinks['networkId']:

            # creating variable for Hub IP and setting public IP to that
            site_1_hub_ip = uplinks['uplinks'][0]['publicIp']

            # creating variable for hub serial
            site_1_hub_serial = uplinks['serial']

        elif site_2_hub_id == uplinks['networkId']:

            # creating variable for Hub IP and setting public IP to that
            site_2_hub_ip = uplinks['uplinks'][0]['publicIp']

            # creating variable for hub serial
            site_2_hub_serial = uplinks['serial']

# creating function to fetch ICMP stats for organization
def get_meraki_icmp_stats():


    # creating dictionary containg all results for all paths that we later append to
    meraki_metric_results_dictionary = {
        'branch_1_to_branch_2_results': {'results': '', 'latency_avg': '', 'loss_avg': ''},
        'branch_1_to_hub_1_results': {'results': '', 'latency_avg': '', 'loss_avg': ''},
        'branch_2_to_branch_1_results': {'results': '', 'latency_avg': '', 'loss_avg': ''},
        'branch_2_to_hub_2_results': {'results': '', 'latency_avg': '', 'loss_avg': ''},
        'hub_1_to_branch_1_results': {'results': '', 'latency_avg': '', 'loss_avg': ''},
        'hub_1_to_hub_2_results': {'results': '', 'latency_avg': '', 'loss_avg': ''},
        'hub_2_to_branch_2_results': {'results': '', 'latency_avg': '', 'loss_avg': ''},
        'hub_2_to_hub_1_results': {'results': '', 'latency_avg': '', 'loss_avg': ''}
    }

    meraki_metric_results_dictionary['branch_1_to_branch_2_results']['results'] = MerakiConfig.\
        meraki_dashboard.devices.getDeviceLossAndLatencyHistory(
            MerakiConfig.site_1_branch_serial, MerakiConfig.site_2_branch_ip
            )

    meraki_metric_results_dictionary['branch_1_to_hub_1_results']['results'] = MerakiConfig.\
        meraki_dashboard.devices.getDeviceLossAndLatencyHistory(
            MerakiConfig.site_1_branch_serial, MerakiConfig.site_1_hub_ip
            )

    meraki_metric_results_dictionary['branch_2_to_branch_1_results']['results'] = MerakiConfig.\
        meraki_dashboard.devices.getDeviceLossAndLatencyHistory(
            MerakiConfig.site_2_branch_serial, MerakiConfig.site_1_branch_ip
            )

    meraki_metric_results_dictionary['branch_2_to_hub_2_results']['results'] = MerakiConfig.\
        meraki_dashboard.devices.getDeviceLossAndLatencyHistory(
            MerakiConfig.site_2_branch_serial, MerakiConfig.site_2_hub_ip
            )

    meraki_metric_results_dictionary['hub_1_to_branch_1_results']['results'] = MerakiConfig.\
        meraki_dashboard.devices.getDeviceLossAndLatencyHistory(
            MerakiConfig.site_1_hub_serial, MerakiConfig.site_1_branch_ip
            )

    meraki_metric_results_dictionary['hub_1_to_hub_2_results']['results'] = MerakiConfig.\
        meraki_dashboard.devices.getDeviceLossAndLatencyHistory(
            MerakiConfig.site_1_hub_serial, MerakiConfig.site_2_hub_ip
            )

    meraki_metric_results_dictionary['hub_2_to_branch_2_results']['results'] = MerakiConfig.\
        meraki_dashboard.devices.getDeviceLossAndLatencyHistory(
            MerakiConfig.site_2_hub_serial, MerakiConfig.site_2_branch_ip
            )

    meraki_metric_results_dictionary['hub_2_to_hub_1_results']['results'] = MerakiConfig.\
        meraki_dashboard.devices.getDeviceLossAndLatencyHistory(
            MerakiConfig.site_2_hub_serial, MerakiConfig.site_1_hub_ip
            )

# iterating through each name of the dictionary
    for result_name in meraki_metric_results_dictionary:

        # creating two lists that will hold all of the latency/loss values
        result_latency_list = []
        result_loss_list = []

        # iterating through the meraki_metric_results_dictionary results list to retrieve all 
        # latency/loss values across all timestampls and append them to the lists that were 
        # created above for each result group
        for results in meraki_metric_results_dictionary[result_name]['results']:

            # applying filter to make sure that the value is not None
            if results['latencyMs'] != None:

                result_latency_list.append(results['latencyMs'])

            # applying filter to make sure that the value is not None
            elif results['lossPercent'] != None:

                result_loss_list.append(results['lossPercent'])

            # applying filter to make sure that the value is not None
            elif results['lossPercent'] == None:

                result_loss_list.append(0.0)


        meraki_metric_results_dictionary[result_name]['latency_avg'] = mean(result_latency_list)
        print(result_name)
        print(mean(result_latency_list))
        #meraki_metric_results_dictionary[result_name]['loss_avg'] = sum(result_loss_list) / len(result_loss_list)



    return meraki_metric_results_dictionary

        

# creating variable that is the dictionary result of the get_meraki_icmp_stats function
meraki_probe_test_results_dictionary = get_meraki_icmp_stats()
#print(meraki_probe_test_results_dictionary)




# need to start mapping in vpn paths vs not in vpn paths
# starting off with average that will be listed below
# in order to account for latency in both directions we will take the average of both directions

# site 1 to site 2 branch is listed below averages calculated both ways
branch_to_branch_latency_average = (meraki_probe_test_results_dictionary['branch_1_to_branch_2_results']['latency_avg'] \
    + meraki_probe_test_results_dictionary['branch_2_to_branch_1_results']['latency_avg']) // 2

# site 1 to site 2 through Middle Mile is captured below
branch_to_branch__mmo_latency_average = ((
    meraki_probe_test_results_dictionary['branch_1_to_hub_1_results']['latency_avg'] + \
        meraki_probe_test_results_dictionary['hub_1_to_hub_2_results']['latency_avg'] + \
            meraki_probe_test_results_dictionary['hub_2_to_branch_2_results']['latency_avg']) + \
                (meraki_probe_test_results_dictionary['branch_2_to_hub_2_results']['latency_avg'] + \
                    meraki_probe_test_results_dictionary['hub_2_to_hub_1_results']['latency_avg'] + \
                        meraki_probe_test_results_dictionary['hub_1_to_branch_1_results']['latency_avg'] 
                        )) // 2


test_results_dictionary_latency = {
        'branch_1_to_branch_2_results': '',
        'branch_1_to_hub_1_results': '',
        'branch_2_to_branch_1_results': '',
        'branch_2_to_hub_2_results': '',
        'hub_1_to_branch_1_results': '',
        'hub_1_to_hub_2_results': '',
        'hub_2_to_branch_2_results': '',
        'hub_2_to_hub_1_results': ''
    }

for metrics in meraki_probe_test_results_dictionary:

    # entering in 1440 min as that accounts for 24 hours (for now inputting 360 for last few hours)
    temp_list = meraki_probe_test_results_dictionary[metrics]['results'][-1200:]

    # creating lists containg latency and loss
    latency_results = []
    loss_results = []

    # iterating through temp list of indexed results above
    for test_metric in temp_list:

        latency_results.append(test_metric['latencyMs'])

    # using list comprehension 
    # to remove None values in list 
    filtered_latency_results = [i for i in latency_results if i] 

    test_results_dictionary_latency[metrics] = filtered_latency_results



# Using map() and add()
# Add corresponding elements of two lists
branch_to_branch_added_list_results = list(map(add, test_results_dictionary_latency\
    ['branch_1_to_branch_2_results'], test_results_dictionary_latency['branch_1_to_branch_2_results']))

# Use a list comprehension for a more compact implementation and dividing each element by 2 since we 
# added the latency to and from the branch
branch_to_branch_final_list_results = [number / 2 for number in branch_to_branch_added_list_results]

print(branch_to_branch_final_list_results)

# creating variable to hold rows for latency results
branch_to_branch_rows = []


count = 0

for x in branch_to_branch_final_list_results:
    count = count + 1
    branch_to_branch_rows.append(count)


# Using map() and add()
# Add corresponding elements of two lists
branch_1_to_branch_2_added_vpn_list_results = list(map(sum, zip(test_results_dictionary_latency\
    ['branch_1_to_hub_1_results'], test_results_dictionary_latency['hub_1_to_hub_2_results'],\
        test_results_dictionary_latency['hub_2_to_branch_2_results'])))

branch_2_to_branch_1_added_vpn_list_results = list(map(sum, zip(test_results_dictionary_latency \
    ['branch_2_to_hub_2_results'], test_results_dictionary_latency['hub_2_to_hub_1_results'], \
        test_results_dictionary_latency['hub_1_to_branch_1_results'])))

# Using map() and add()
# Add corresponding elements of two lists
branch_to_branch_latency_both_directions =  list(map(add, branch_1_to_branch_2_added_vpn_list_results, \
    branch_2_to_branch_1_added_vpn_list_results))

# Use a list comprehension for a more compact implementation and dividing each element by 6 since we 
# added the latency to and from the branch
branch_to_branch_vpn_final_list_results = [number / 2 for number in branch_to_branch_latency_both_directions]

print("look below")

print(branch_to_branch_vpn_final_list_results)

# creating variable to hold rows for latency results
branch_to_branch_in_vpn_rows = []


count = 0

for x in branch_to_branch_vpn_final_list_results:
    count = count + 1
    branch_to_branch_in_vpn_rows.append(count)

















x_axis_list = ['in_vpn', 'not_in_vpn']

y_axis = [float(branch_to_branch__mmo_latency_average), float(branch_to_branch_latency_average)]





####### the code below section calculates average jitter across all tests

# x-coordinates of left sides of bars  
#left = [1, 2] 
  
# heights of bars 
#height = y_axis
#height = [1, 2, 3, 4, 5, 6, 7]
  
# labels for bars 
#tick_label = x_axis_list 
  
# plotting a bar chart 
#plt.bar(left, height, tick_label = tick_label, 
#        width = 0.8, color = ['red', 'green']) 
  
# naming the x-axis 
#plt.xlabel('Difference in VPN vs not in VPN') 
# naming the y-axis 
#plt.ylabel('Latency Average') 
# plot title 
#plt.title('Average Latency Across Umbrella vs Internet') 
  
# function to show the plot 
#plt.show() 






def get_latency_plot_graph():
    
    # line 1 points 
    x1 = numpy.array(branch_to_branch_rows)
    y1 = numpy.array(branch_to_branch_final_list_results)
    # plotting the line 2 points  
    plt.plot(x1, y1, label = "Branch to Branch Direct Latency") 




    # line 2 points 
    x2 = numpy.array(branch_to_branch_in_vpn_rows)
    y2 = numpy.array(branch_to_branch_vpn_final_list_results)
    # plotting the line 2 points  
    plt.plot(x2, y2, label = "In VPN Branch to Branch Latency") 



    # naming the x axis 
    plt.xlabel('units in time') 
    # naming the y axis 
    plt.ylabel('Latency in MS') 
    # giving a title to my graph 
    plt.title('Latency Difference Between No VPN and VPN') 
    
    # show a legend on the plot 
    plt.legend() 
    
    # function to show the plot 
    plt.show() 

get_latency_plot_graph()
