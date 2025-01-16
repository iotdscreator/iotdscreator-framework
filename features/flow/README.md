# Flow Features
IoTDSCreator extracts 41 flow features, described below. The direction ("forward" and "backward") is determined by the initial packet. The "forward" is the direction from a source address of the first packet to a destination address of the first packet. The "backward" is the opposite direction.

<table>
  <tr>
    <td align="center"><b>Name</b></td><td align="center"><b>Description</b></td>
  </tr>
  <tr>
    <td>backward_iat_max</td><td>The maximum of the inter-arrival time between packets within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>backward_iat_mean</td><td>The mean of the inter-arrival time between packets within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>backward_iat_min</td><td>The minimum of the inter-arrival time between packets within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>backward_iat_std</td><td>The standard deviation of the inter-arrival time between packets within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>backward_iat_total</td><td>The total of the inter-arrival time between packets within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>backward_packet_length_max</td><td>The maximum length of the packet within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>backward_packet_length_mean</td><td>The mean length of the packet within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>backward_packet_length_min</td><td>The minimum length of the packet within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>backward_packet_length_std</td><td>The standard deviation of the packet within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>bpkts_per_second</td><td>The number of packets per second within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>flow_ack</td><td>The number of ACKs enabled within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_cwr</td><td>The number of CWRs enabled within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_ece</td><td>The number of ECEs enabled within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_fin</td><td>The number of FINs enabled within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_iat_max</td><td>The maximum of the inter-arrival time between packets within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_iat_mean</td><td>The mean of the inter-arrival time between packets within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_iat_min</td><td>The minimum of the inter-arrival time between packets within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_iat_std</td><td>The standard deviation of the inter-arrival time between packets within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_iat_total</td><td>The total of the inter-arrival time between packets within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_packets_per_second</td><td>The number of packets per second within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_protocol</td><td>The transport protocol of the flow.</td>
  </tr>
  <tr>
    <td>flow_psh</td><td>The number of PSHs enabled within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_rst</td><td>The number of RSTs enabled within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_syn</td><td>The number of SYNs enabled within a window in the both direction.</td>
  </tr>
  <tr>
    <td>flow_urg</td><td>The number of URGs enabled within a window in the both direction.</td>
  </tr>
  <tr>
    <td>forward_iat_max</td><td>The maximum of the inter-arrival time between packets within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>forward_iat_mean</td><td>The mean of the inter-arrival time between packets within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>forward_iat_min</td><td>The minimum of the inter-arrival time between packets within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>forward_iat_std</td><td>The standard deviation of the inter-arrival time between packets within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>forward_iat_total</td><td>The total of the inter-arrival time between packets within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>forward_packet_length_max</td><td>The maximum length of the packet within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>forward_packet_length_mean</td><td>The mean length of the packet within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>forward_packet_length_min</td><td>The minimum length of the packet within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>forward_packet_length_std</td><td>The standard deviation of the packet within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>fpkts_per_second</td><td>The number of packets per second within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>total_backward_packets</td><td>The total number of packets within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>total_bhlen</td><td>The total length of headers of packets within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>total_fhlen</td><td>The total length of headers of packets within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>total_forward_packets</td><td>The total number of packets within a window in the forward direction.</td>
  </tr>
  <tr>
    <td>total_length_of_backward_packets</td><td>The total length of packets within a window in the backward direction.</td>
  </tr>
  <tr>
    <td>total_length_of_forward_packets</td><td>The total length of packets within a window in the forward direction.</td>
  </tr>
</table>
