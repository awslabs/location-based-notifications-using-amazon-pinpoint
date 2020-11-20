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

import React, { Component }from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';

import "./App.css";
import "@aws-amplify/ui/dist/style.css";

import Amplify, {Auth} from 'aws-amplify';
import aws_exports from './aws-exports';

import { 
  ConfirmSignIn, 
  ConfirmSignUp, 
  ForgotPassword, 
  RequireNewPassword, 
  SignIn, 
  VerifyContact, 
  withAuthenticator ,
  AmplifyTheme
} from 'aws-amplify-react';

import CustomSignUp from './components/CustomSignUp'
import GeofenceNavBar from './components/GeofenceNavBar'
import GeofenceHome from './components/GeofenceHome';
import GeofenceDetails from './components/GeofenceDetails';
import GeofenceEdit from './components/GeofenceEdit';

Amplify.configure({
  Auth: {
    region: aws_exports.aws_project_region,
    userPoolId: aws_exports.user_pool_id,
    userPoolWebClientId: aws_exports.user_pool_web_client_id,
    identityPoolId: aws_exports.identity_pool_id,
    identityPoolRegion: aws_exports.aws_project_region
  },
  Analytics: {
    AWSPinpoint: {
      appId: aws_exports.pinpoint_app_id,
      region: aws_exports.aws_project_region,
    }
  },
  API: {
    aws_appsync_graphqlEndpoint: aws_exports.aws_appsync_graphqlEndpoint,
    aws_appsync_region: aws_exports.aws_project_region,
    aws_appsync_authenticationType: aws_exports.aws_appsync_authenticationType
	}
})

class App extends Component {
  state = {
    loggedUser: ""
  };

  async componentDidMount() {
    await Auth.currentAuthenticatedUser().then(user => {
      this.setState({
        loggedUser: user.username
      });
    });
  }

  render() {
    return (
      <div>
        <GeofenceNavBar loggedUser={this.state.loggedUser} />  
        <Router>          
          <Switch>
            <Route path="/" component={GeofenceHome} exact />            
            <Route path="/geofenceDetails" component={GeofenceDetails} />
            <Route path="/geofenceEdit" component={GeofenceEdit} />
            <Route component={Error} />
          </Switch>
        </Router>
      </div>
    );
  }
}

const MyTheme = {
  ...AmplifyTheme
};

export default withAuthenticator(
  App, 
  true, 
  [
    <SignIn/>,
    <ConfirmSignIn/>,
    <VerifyContact/>,
    <CustomSignUp override={'SignUp'} />,
    <ConfirmSignUp/>,
    <ForgotPassword/>,
    <RequireNewPassword />
  ], 
  null, 
  MyTheme
);
