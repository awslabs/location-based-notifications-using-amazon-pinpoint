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

import React, { Component } from 'react';

import KeyboardBackspaceIcon from '@material-ui/icons/KeyboardBackspace';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import MenuItem from '@material-ui/core/MenuItem';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField'
import Select from '@material-ui/core/Select';
import SaveIcon from '@material-ui/icons/Save';
import DeleteIcon from '@material-ui/icons/Delete';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';

import { Link } from 'react-router-dom';
import { API, graphqlOperation } from 'aws-amplify';
import { getGeofenceMessage } from '../graphql/queries';
import { createGeofenceMessage, deleteGeofenceMessage } from '../graphql/mutations'
import { Box } from '@material-ui/core';

class GeofenceDetails extends Component { 

  state = {
    id: "",
    name: "",
    branch: "",
    address: "",
    city: "",
    country: "",
    region: "",
    latitude: "",
    longitude: "",
    defType: "",
    defValue: "",
    title: "",
    body: "",
    service: "",
    statusMsg: "",
    premiumTitle: "",
    premiumBody: "",
    premiumService: "",
    statusPremiumMsg: ""
  };

  componentDidMount() {
    let id = ''
    if (this.props.location.obj != null) {
      id = this.props.location.obj.id

      let def = this.props.location.obj.definition
      let splitDef

      if (def != null) {
        splitDef = def.split(':')
      }

      this.setState({
        id: id,
        name: this.props.location.obj.name,
        branch: this.props.location.obj.branch,
        address: this.props.location.obj.address,
        city: this.props.location.obj.city,
        country: this.props.location.obj.country,
        region: this.props.location.obj.region,
        latitude: this.props.location.obj.latitude,
        longitude: this.props.location.obj.longitude,
        defType: splitDef[0],
        defValue: splitDef[1].slice(1,-1)
      })
    }  
    
    this.queryGeofenceMessages(id);   
  }

  queryGeofenceMessages = async (id) => {
    try {
      let geofenceMessage = await API.graphql(graphqlOperation(
        getGeofenceMessage, {
          template: id
        }
      ));
      let message = geofenceMessage.data.getGeofenceMessage.message;
      console.log('Get Geofence Message Response =>' + JSON.stringify(message, null, 4));

      this.setState({
        title: message.title,
        body: message.body,
        service: message.service
      });    
    } catch (err) {
      console.error('Err Geofence Message => ' + JSON.stringify(err, null, 4))
    }  
    
    try {
      let premiumGeofenceMessage = await API.graphql(graphqlOperation(
        getGeofenceMessage, {
          template: `${id}-PREMIUM`
        }
      ));

      let premiumMessage = premiumGeofenceMessage.data.getGeofenceMessage.message;
      console.log('Get Premium Geofence Message Response =>' + JSON.stringify(premiumMessage, null, 4));

      this.setState({
        premiumTitle: premiumMessage.title,
        premiumBody: premiumMessage.body,
        premiumService: premiumMessage.service
      });

    } catch (err) {
      console.error('Err Premium Geofence Message => ' + JSON.stringify(err, null, 4))
    }
  };

  change = e => {
    this.setState({
      [e.target.name]: e.target.value
    });
  };

  createGeofenceMessage = async (e) => {
    e.preventDefault();

    const {id, title, body, service} = this.state
    
    let resultcreateGeofenceMessage = await API.graphql(graphqlOperation(
      createGeofenceMessage, {
        template: id,
        input: {
          service: service,
          action: "OPEN_APP",
          title: title,
          body: body
        }
      }
    ));

    this.setState({
      statusMsg: "Geofence message created successfully!"
    })

    console.log('Create Geofence Message Response =>' + JSON.stringify(resultcreateGeofenceMessage, null, 4));
  };

  deleteGeofenceMessage = async (e) => {
    e.preventDefault();

    const {id} = this.state

    let resultDeleteGeofenceMessage = await API.graphql(graphqlOperation(
      deleteGeofenceMessage, {
        template: id
      }
    ));
    console.log('Delete Geofence Message Response =>' + JSON.stringify(resultDeleteGeofenceMessage, null, 4));

    this.setState({
      title: "",
      body: "",
      service: "",
      statusMsg: "Geofence message deleted successfully!"
    });
  };

  createPremiumGeofenceMessage = async (e) => {
    e.preventDefault();

    const {id, premiumTitle, premiumBody, premiumService} = this.state

    let resultcreatePremiumGeofenceMessage = await API.graphql(graphqlOperation(
      createGeofenceMessage, {
        template: `${id}-PREMIUM`,
        input: {
          service: premiumService,
          action: "OPEN_APP",
          title: premiumTitle,
          body: premiumBody
        }
      }
    ));

    console.log('Create Premium Geofence Message Response =>' + JSON.stringify(resultcreatePremiumGeofenceMessage, null, 4));

    this.setState({
      statusPremiumMsg: "Premium geofence message created successfully!"
    })
  };

  deletePremiumGeofenceMessage = async (e) => {
    e.preventDefault();

    const {id} = this.state

    let resultDeletePremiumGeofenceMessage = await API.graphql(graphqlOperation(
      deleteGeofenceMessage, {
        template: `${id}-PREMIUM`
      }
    ));
    console.log('Delete Premium Geofence Message Response =>' + JSON.stringify(resultDeletePremiumGeofenceMessage, null, 4));

    this.setState({
      premiumTitle: "",
      premiumBody: "",
      premiumService: "",
      statusPremiumMsg: "Premium geofence message deleted successfully!"
    });
  };

  render() {    
    return (
      <div>
        <div>
          <div>
            
            <br/>

            <Link to="/" style={{ textDecoration: 'none' }}>
              <Button
                style={{ backgroundColor: '#337ab7', margin: (10) }}
                variant="contained" 
                color="primary"
                startIcon={<KeyboardBackspaceIcon />}        
              >
              Back  
              </Button>          
            </Link>

            <br/>
            <br/>

            <Box 
              fontWeight="fontWeightMedium" 
              fontFamily="tahoma"
              lineHeight={2} m={1} 
              border={1} 
              borderColor="#337ab7" 
              borderRadius={20} 
              width={600}
              margin="auto"
              padding={2}
              style={{ color: '#337ab7'}}
              boxShadow={[10, 5, 5]}
            >
              <p align="center" style={{ fontSize: 20, color: "#337ab7", margin: "auto", fontWeight: "bold" }}>
                {this.state.name} - {this.state.branch}
              </p>
              Address: {this.state.address}
              <br/>
              Location: {this.state.city} - {this.state.region} / {this.state.country}
              <br/>
              Latitude: {this.state.latitude}
              <br/>
              Longitude: {this.state.longitude}
              <br/>
              <Box
                fontWeight="fontWeightMedium" 
                fontFamily="tahoma"
                lineHeight={2} m={1} 
                borderRadius={20} 
                width={580}
                margin="left"
                padding={1}
                style={{ backgroundColor: '#eceff1'}}>
                Definition Type: {this.state.defType}
                <br/>
                Definition Value: {this.state.defValue}
              </Box>
              </Box>
            <br/>
            <br/>
            <br/>

          <Grid container direction="row" spacing={6} justify="center">  
            <Grid item xs={5}> 
              <Card>
                <CardContent>
                  
                  <Typography  color="textSecondary" gutterBottom>
                    Add Message for this geofence
                  </Typography>
                  
                  <Typography color="textSecondary">
                    <form>
                      <TextField
                        name="title"
                        label="Title"
                        fullWidth="true"
                        value={this.state.title}
                        onChange={e => this.change(e)}
                      />
                      <br/>
                      <TextField
                        name="body"
                        label="Body"
                        fullWidth="true"
                        multiline
                        value={this.state.body}
                        onChange={e => this.change(e)}
                      />
                      <br/>
                      <FormControl fullWidth="true">
                        <InputLabel>Service</InputLabel>
                        <Select
                          name="service"
                          label="Service"
                          fullWidth="true"
                          value={this.state.service}
                          onChange={e => this.change(e)}
                          >
                          <MenuItem value={`APNS`}>APNS</MenuItem>
                          <MenuItem value={`GCM`}>GCM</MenuItem>
                        </Select>
                      </FormControl>
                      <br/>
                      <br/>
                      <Grid
                        container
                        direction="row"
                        justify="space-evenly"
                        alignItems="center"
                      >
                        <Button
                          style={{ backgroundColor: '#337ab7' }} 
                          variant="contained" 
                          color="primary"
                          startIcon={<SaveIcon />}
                          onClick={e => this.createGeofenceMessage(e)}>
                            Add Message
                        </Button>
                        <Button 
                          style={{ backgroundColor: '#337ab7' }} 
                          variant="contained" 
                          color="primary"
                          startIcon={<DeleteIcon />}
                          onClick={e => this.deleteGeofenceMessage(e)}>
                            Delete Message
                        </Button>
                        <p>{this.state.statusMsg}</p>
                      </Grid>
                    </form>
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          
            <Grid item xs={5}> 
              <Card>
                <CardContent>
                  
                  <Typography  color="textSecondary" gutterBottom>
                    Add Premium Message for this geofence
                  </Typography>
                  
                  <Typography color="textSecondary">
                    <form>
                      <TextField
                        name="premiumTitle"
                        label="Title"
                        fullWidth="true"
                        value={this.state.premiumTitle}
                        onChange={e => this.change(e)}
                      />
                      <br/>
                      <TextField
                        name="premiumBody"
                        label="Body"
                        fullWidth="true"
                        multiline
                        value={this.state.premiumBody}
                        onChange={e => this.change(e)}
                      />
                      <br/>
                      <FormControl fullWidth="true">
                        <InputLabel>Service</InputLabel>
                        <Select
                          name="premiumService"
                          label="Service"
                          value={this.state.premiumService}
                          onChange={e => this.change(e)}
                          >
                          <MenuItem value={`APNS`}>APNS</MenuItem>
                          <MenuItem value={`GCM`}>GCM</MenuItem>
                        </Select>
                      </FormControl>
                      <br/>
                      <br/>
                      <Grid
                        container
                        direction="row"
                        justify="space-evenly"
                        alignItems="center"
                      >
                        <Button 
                          style={{ backgroundColor: '#337ab7' }}
                          variant="contained" 
                          color="primary"
                          startIcon={<SaveIcon />}
                          onClick={e => this.createPremiumGeofenceMessage(e)}>
                            Add Premium Message
                        </Button>
                        <Button 
                          style={{ backgroundColor: '#337ab7' }}
                          variant="contained" 
                          color="primary"
                          startIcon={<DeleteIcon />}
                          onClick={e => this.deletePremiumGeofenceMessage(e)}>
                            Delete Premium Message
                        </Button>
                        <p>{this.state.statusPremiumMsg}</p>
                      </Grid>
                    </form>
                  </Typography>
                  
                </CardContent>
              </Card>
            </Grid>
          </Grid>  

          </div>
        </div>
      </div>
    );
  }

}

export default GeofenceDetails;