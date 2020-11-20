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
import TextField from '@material-ui/core/TextField'
import Button from '@material-ui/core/Button';
import SaveIcon from '@material-ui/icons/Save';
import Grid from '@material-ui/core/Grid';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';

import { Link } from 'react-router-dom';
import { API, graphqlOperation } from 'aws-amplify';
import { updateGeofence } from '../graphql/mutations'

class GeofenceEdit extends Component { 

  state = {
    id: "",
    name: "",
    branch: "",
    definition: "",
    defType: "",
    defValue: ""
  };

  componentDidMount() {
    if (this.props.location.obj != null) {
      let def = this.props.location.obj.definition
      let splitDef

      if (def != null) {
        splitDef = def.split(':')
      }

      this.setState({
        id: this.props.location.obj.id,
        name: this.props.location.obj.name,
        branch: this.props.location.obj.branch,
        defType: splitDef[0],
        defValue: splitDef[1].slice(1,-1)
      })
    }  
  }

  updateGeofence = async () => {
    let geofenceUpdateResponse = await API.graphql(graphqlOperation(
      updateGeofence, {
        input: {
          id: this.state.id,
          name: this.state.name,
          branch: this.state.branch,
          definition: this.state.defType + ':(' + this.state.defValue + ')',
        }
      }
    ));
    console.log('Geofence Update Response =>' + JSON.stringify(geofenceUpdateResponse, null, 4));

    this.props.location.queryGeofences()
  };

  change = e => {
    this.setState({
      [e.target.name]: e.target.value
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

            <Grid container 
              direction="row" 
              spacing={6} 
              justify="center">  
            <Grid item xs={6}> 
              <Card>
                <CardContent>
                  <Typography color="textSecondary">
                    <form>
                      <TextField
                        name="name"
                        label="Name"
                        fullWidth="true"
                        value={this.state.name}
                        onChange={e => this.change(e)}
                      />
                      <br/>
                      <TextField
                        name="branch"
                        label="Branch"
                        fullWidth="true"
                        value={this.state.branch}
                        onChange={e => this.change(e)}
                      />
                      <br/>
                      <Grid container 
                        spacing={12}
                        justify="space-between"
                        alignItems="center">
                        <Grid item sm={3}>
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

                      <Grid
                        container
                        direction="row"
                        justify="space-evenly"
                        alignItems="center"
                      >
                        
                        <Link to="/" style={{ textDecoration: 'none' }}>
                          <br/>
                          <Button 
                            style={{ backgroundColor: '#337ab7' }}
                            variant="contained" 
                            color="primary"
                            startIcon={<SaveIcon />}
                            onClick={e => this.updateGeofence(e)}>
                              Update Geofence
                          </Button>
                        </Link>
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

export default GeofenceEdit;