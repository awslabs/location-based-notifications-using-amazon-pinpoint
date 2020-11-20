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

import React from 'react';

import { Auth } from 'aws-amplify';
import {
    SignUp,
    FormSection,
    SectionHeader,
    SectionBody,
    SectionFooter,
    InputRow,
    Link,
    Button
} from 'aws-amplify-react';

export default class MySignUp extends SignUp {

    signUp() {
        const { username, password, email } = this.inputs;

        const param = {
          "username": username,
          "password": password,
          "attributes": {
            "email": email,
            "custom:userType" : "ADMIN"  
          }
        }

        Auth.signUp(param)
            .then(() => this.changeState('confirmSignUp', username))
            .catch(err => this.error(err));
    }

    showComponent(theme) {
      const { hide } = this.props;
        if (hide && hide.includes(MySignUp)) { return null; }

        return (
          <div style={Object.assign({position: 'absolute', left: '25%', top: '20%'}, theme.col6)}>
            <FormSection theme={theme}>
                <SectionHeader theme={theme}>{'Sign Up Account'}</SectionHeader>
                <SectionBody theme={theme}>
                <InputRow
                        autoFocus
                        placeholder={'Username'}
                        theme={theme}
                        key="username"
                        name="username"
                        onChange={this.handleInputChange}
                    />
                    <InputRow
                        placeholder={'Password'}
                        theme={theme}
                        type="password"
                        key="password"
                        name="password"
                        onChange={this.handleInputChange}
                    />
                    <InputRow
                        placeholder={'Email'}
                        theme={theme}
                        key="email"
                        name="email"
                        onChange={this.handleInputChange}
                    />
                    {/*<ButtonRow onClick={this.signUp} theme={theme}>
                        {'Sign Up'}
                      </ButtonRow>*/}
                </SectionBody>


                <SectionFooter theme={theme}>
                  <span style={Object.assign({textAlign: 'left', fontSize: '14px'}, theme.col6)}>
                      {'Have an account? '}
                      <Link
                        theme={theme}
                        onClick={() => this.changeState('signIn')} >
                        Sign In
                      </Link>
                  </span>
                  <span style={Object.assign({textAlign: 'right'}, theme.col6)}>
                    <Button
                      onClick={this.signUp}
                      theme={theme} >
                      Create Account
                    </Button>
                  </span>
                </SectionFooter>


                {/*<SectionFooter theme={theme}>
                    <div style={theme.col6}>
                        <Link theme={theme} onClick={() => this.changeState('confirmSignUp')}>
                            {'Confirm a Code'}
                        </Link>
                    </div>
                    <div style={Object.assign({textAlign: 'right'}, theme.col6)}>
                        <Link theme={theme} onClick={() => this.changeState('signIn')}>
                            {'Sign In'}
                        </Link>
                    </div>
                    </SectionFooter> */}
            </FormSection>
          </div>
        )
    }
}
