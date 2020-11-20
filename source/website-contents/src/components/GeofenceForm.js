/*******************************************************************************************************************************************
*  Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved                                                                  *
*                                                                                                                                          *
*  Licensed under the MIT No Attribution License (MIT-0) (the ‘License’). You may not use this file except in compliance                   *
*  with the License. A copy of the License is located at                                                                                   *
*                                                                                                                                          *
*      https://opensource.org/licenses/MIT-0                                                                                               *
*                                                                                                                                          *
*  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files        *
*  (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge,     *
*  publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.  *
*  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF      *
*  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR *
*  ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH  * 
*  THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                                                              *
*******************************************************************************************************************************************/

import React from "react";
import TextField from '@material-ui/core/TextField'
import Button from '@material-ui/core/Button';
import SaveIcon from '@material-ui/icons/Save';
import Grid from '@material-ui/core/Grid';
import SearchIcon from '@material-ui/icons/Search';
import IconButton from '@material-ui/core/IconButton';
import Box from '@material-ui/core/Box';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import InputLabel from '@material-ui/core/InputLabel';

import { API, graphqlOperation } from 'aws-amplify';
import { getCoordsFromAddress } from '../graphql/queries';
import { createGeofence } from '../graphql/mutations'

export default class GeofenceForm extends React.Component {
  state = {
    address: "",
    name: "",
    branch: "",
    city: "",
    country: "",
    region: "",
    latitude: "",
    longitude: "",
    defType: "",
    defValue: "",
    searchText: "",
    hideFields: false
  };

  change = e => {
    this.setState({
      [e.target.name]: e.target.value
    });
  };

  onSubmit = async (e) => {
    e.preventDefault();

    let resultcreateGeofence = await API.graphql(graphqlOperation(
      createGeofence, {
        input: {
          name: this.state.name, 
          branch: this.state.branch,
          address: this.state.address,
          city: this.state.city,
          country: this.state.country,
          region: this.state.region,
          latitude: parseFloat(this.state.latitude),
          longitude: parseFloat(this.state.longitude),
          definition: this.state.defType + ':(' + this.state.defValue + ')',
          visits: 0
        }
      }
    ));

    console.log('Create Geofence Response =>' + JSON.stringify(resultcreateGeofence, null, 4));

    this.setState({
      address: "",
      name: "",
      branch: "",
      city: "",
      country: "",
      region: "",
      latitude: "",
      longitude: "",
      defType: "",
      defValue: "",
      searchText: "",
      hideFields: false,
      errorGetAddress: ""
    });

    this.props.queryGeofences()
  };

  searchAddress = async () => {
    try {
      let responseddress = await API.graphql(graphqlOperation( 
        getCoordsFromAddress, {
          address: this.state.searchText
        }
      ));    
  
      this.setState({
        address: responseddress.data.getCoordsFromAddress.street,
        city: responseddress.data.getCoordsFromAddress.city,
        country: responseddress.data.getCoordsFromAddress.country,
        region: responseddress.data.getCoordsFromAddress.state,
        latitude: responseddress.data.getCoordsFromAddress.latitude,
        longitude: responseddress.data.getCoordsFromAddress.longitude,
        hideFields: true,
        errorGetAddress: ""
      })
    } catch (err) {
      console.error('Err Getting the address => ' + JSON.stringify(err, null, 4))
      this.setState({
        errorGetAddress: 'Address not found. Please try again!'
      })
    }
  }

  render() {
    return (
      <div>
        <br/>

        <Box
          border={1} 
          borderColor="#337ab7" 
          borderRadius={50} 
          width={720}
          margin="auto"
          >
          <TextField 
            InputProps={{ disableUnderline: true }}
            style={{ width: 620 }}            
            name="searchText"
            label="Enter an address to register a new geofence"
            value={this.state.searchText}
            onChange={e => this.change(e)}
          />
          
          <IconButton onClick={e => this.searchAddress(e)} color="primary">
            <SearchIcon fontSize="large" style={{ color: '#337ab7'}}/>
          </IconButton>
        </Box>

        <p style={{ fontSize: 14, color: "#ff0000" }}> {this.state.errorGetAddress} </p>

        { this.state.hideFields ? 
        
          <form>
            <br/><br/>
            <Box 
              border={1} 
              borderColor="#337ab7" 
              borderRadius="borderRadius" 
              width={680}
              margin="auto"
              padding={2}
              boxShadow={[10, 5, 5]} >

              <p align="left" style={{ fontSize: 14, color: "#337ab7", margin: "auto" }}>
                  Fill up the fields below:
              </p>

              <Grid container 
                spacing={6} 
                justify="center"
                alignItems="center">   
                <Grid item xs={11}>
                  <TextField required
                    name="name"
                    label="Name"
                    fullWidth={true}
                    value={this.state.name}
                    onChange={e => this.change(e)}
                  />
                  <TextField required
                    name="branch"
                    label="Branch"
                    fullWidth={true}
                    value={this.state.branch}
                    onChange={e => this.change(e)}
                  />
                </Grid>
              </Grid>

              <Grid container 
                spacing={11}
                justify="space-around"
                alignItems="center">
                <Grid item sm={2}>
                  <FormControl fullWidth="true">
                    <InputLabel>Type</InputLabel>
                      <Select
                        name="defType"
                        label="Type"
                        value={this.state.defType}
                        onChange={e => this.change(e)}
                        >
                      <MenuItem value={`RADIUS`}>Radius</MenuItem>
                      <MenuItem value={`POLYGON`}>Polygon</MenuItem>
                    </Select>
                    </FormControl>
                  </Grid>
                  <Grid item sm={8}>
                  <TextField required
                    name="defValue"
                    label="Definition in meters for radius or add all lat/lng for polygon"
                    fullWidth={true}
                    value={this.state.defValue}
                    onChange={e => this.change(e)}
                  />
                  <br/>
                </Grid>
              </Grid>
            </Box>
            <br/><br/>

            <Grid container spacing={6} justify="center" alignItems="center">          
              <Grid item xs={4}>
                <TextField disabled
                  name="address"
                  label="Address"
                  fullWidth={true}
                  value={this.state.address}
                  onChange={e => this.change(e)}
                />
              
                <TextField disabled
                  name="city"
                  label="City"
                  fullWidth={true}
                  value={this.state.city}
                  onChange={e => this.change(e)}
                />

                <TextField disabled
                  name="country"
                  label="Country"
                  fullWidth={true}
                  value={this.state.country}
                  onChange={e => this.change(e)}
                />
              </Grid>

              <Grid item xs={4}>
                <TextField disabled
                  name="region"
                  label="Region"
                  fullWidth={true}
                  value={this.state.region}
                  onChange={e => this.change(e)}
                />
          
                <TextField disabled
                  name="latitude"
                  label="Latitude"
                  fullWidth={true}
                  value={this.state.latitude}
                  onChange={e => this.change(e)}
                />
          
                <TextField disabled
                  name="longitude"
                  label="Longitude"
                  fullWidth={true}
                  value={this.state.longitude}
                  onChange={e => this.change(e)}
                />
              </Grid>
            </Grid>
            
            <Grid item xs={12}>
              <br/>
              <Button style={{ background: '#337ab7'}}
                variant="contained" 
                color="primary"
                startIcon={<SaveIcon />}
                onClick={e => this.onSubmit(e)}>
                  Create Geofence
              </Button>
            </Grid>
          </form>

        : null }

      </div>
    );
  }
}