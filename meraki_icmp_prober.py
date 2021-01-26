import requests
import json
import meraki
from numpy import mean
import matplotlib.pyplot as plt



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

        elif site_2_branch_id == uplinks['networkId']:

            # creating variable for branch IP and setting public IP to that
            site_2_branch_ip = uplinks['uplinks'][0]['publicIp']

        elif site_1_hub_id == uplinks['networkId']:

            # creating variable for Hub IP and setting public IP to that
            site_1_hub_ip = uplinks['uplinks'][0]['publicIp']

        elif site_2_hub_id == uplinks['networkId']:

            # creating variable for Hub IP and setting public IP to that
            site_2_hub_ip = uplinks['uplinks'][0]['publicIp']

# creating function to fetch ICMP stats for organization
def get_meraki_icmp_stats():

    # using meraki sdk to obtain icmp metrics for the meraki network IDs in MerakiConfig
    meraki_icmp_metrics_response = MerakiConfig.meraki_dashboard.organizations.\
        getOrganizationDevicesUplinksLossAndLatency(
            MerakiConfig.meraki_org_id
        )

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

    # iterating through meraki_icmp_metrics_response to start mapping the different measurement paths
    for results in meraki_icmp_metrics_response:

        # setting conditional statement to match network ID with branch site 1
        if MerakiConfig.site_1_branch_id == results['networkId']:

            # setting conditional statement to match based on branch site 2
            if results['ip'] == MerakiConfig.site_2_branch_ip:

                # updating dictionary key value for meraki_metric_results_dictionary
                meraki_metric_results_dictionary['branch_1_to_branch_2_results']['results'] = results['timeSeries']

            # setting conditional statement to match site 1 hub
            elif results['ip'] == MerakiConfig.site_1_hub_ip:

                # updating dictionary key value for meraki_metric_results_dictionary
                meraki_metric_results_dictionary['branch_1_to_hub_1_results']['results'] = results['timeSeries']


        # setting conditional statement to match network ID with branch site 2
        elif MerakiConfig.site_2_branch_id == results['networkId']:

            # setting conditional statement to match based on branch site 1
            if results['ip'] == MerakiConfig.site_1_branch_ip:

                # updating meraki_metric_results_dictionary with timeseries results
                meraki_metric_results_dictionary['branch_2_to_branch_1_results']['results'] = results['timeSeries']

            # setting conditional statement to match site 2 hub
            elif results['ip'] == MerakiConfig.site_2_hub_ip:

                # updating meraki_metric_results_dictionary with timeseries results
                meraki_metric_results_dictionary['branch_2_to_hub_2_results']['results'] = results['timeSeries']

        # setting conditional statement to match network ID with site 1 Hub
        elif MerakiConfig.site_1_hub_id == results['networkId']:

            # setting conditional statement to match based on branch site 1
            if results['ip'] == MerakiConfig.site_1_branch_ip:

                # updating meraki_metric_results_dictionary with timeseries results
                meraki_metric_results_dictionary['hub_1_to_branch_1_results']['results'] = results['timeSeries']

            # setting conditional statement to match site 2 hub
            elif results['ip'] == MerakiConfig.site_2_hub_ip:

                # updating meraki_metric_results_dictionary with timeseries results
                meraki_metric_results_dictionary['hub_1_to_hub_2_results']['results'] = results['timeSeries']


        # setting conditional statement to match network ID with site 2 Hub
        elif MerakiConfig.site_2_hub_id == results['networkId']:

            # setting conditional statement to match based on branch site 2
            if results['ip'] == MerakiConfig.site_2_branch_ip:

                # updating meraki_metric_results_dictionary with timeseries results
                meraki_metric_results_dictionary['hub_2_to_branch_2_results']['results'] = results['timeSeries']

            # setting conditional statement to match site 1 hub
            elif results['ip'] == MerakiConfig.site_1_hub_ip:

                # updating meraki_metric_results_dictionary with timeseries results
                meraki_metric_results_dictionary['hub_2_to_hub_1_results']['results'] = results['timeSeries']




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
        print(mean(result_loss_list))
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

print(branch_to_branch_latency_average)

# site 1 to site 2 through Middle Mile is captured below
branch_to_branch__mmo_latency_average = ((
    meraki_probe_test_results_dictionary['branch_1_to_hub_1_results']['latency_avg'] + \
        meraki_probe_test_results_dictionary['hub_1_to_hub_2_results']['latency_avg'] + \
            meraki_probe_test_results_dictionary['hub_2_to_branch_2_results']['latency_avg']) + \
                (meraki_probe_test_results_dictionary['branch_2_to_hub_2_results']['latency_avg'] + \
                    meraki_probe_test_results_dictionary['hub_2_to_hub_1_results']['latency_avg'] + \
                        meraki_probe_test_results_dictionary['hub_1_to_branch_1_results']['latency_avg'] 
                        )) // 2


print(branch_to_branch__mmo_latency_average)




x_axis_list = ['in_vpn', 'not_in_vpn']


print(x_axis_list)

y_axis = [float(branch_to_branch__mmo_latency_average), float(branch_to_branch_latency_average)]
    
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
ax.bar(x_axis_list,y_axis)
plt.show()

