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
</table>
