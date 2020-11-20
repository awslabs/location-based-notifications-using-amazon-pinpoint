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

import React from 'react'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import Typography from '@material-ui/core/Typography'
import MenuItem from '@material-ui/core/MenuItem';
import Menu from '@material-ui/core/Menu';
import IconButton from '@material-ui/core/IconButton';
import AccountCircle from '@material-ui/icons/AccountCircle';
import { makeStyles } from '@material-ui/core/styles';

import {Auth} from 'aws-amplify';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  menuButton: {
    marginRight: theme.spacing(2),
  },
  title: {
    flexGrow: 1,
  },
}));

const GeofenceNavBar = ({loggedUser}) => {
  const classes = useStyles();

  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  const signOut = () => {
    Auth.signOut().then(() => {
      console.log("signout executed");
    });
  };

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return(
    <div className={classes.root}>
      <AppBar position="static" style={{ background: '#337ab7' }}>
        <Toolbar>
          <Typography variant="h6" className={classes.title}>
              Geofence - Portal Admin
          </Typography>
          


          <div>
            <IconButton
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
            <AccountCircle />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={open}
              onClose={handleClose}
            >
              <MenuItem disabled>User: {loggedUser}</MenuItem>
              <MenuItem onClick={signOut}>Logout</MenuItem>
            </Menu>
          </div>  



        </Toolbar>
      </AppBar>
    </div>
  )
}

export default GeofenceNavBar;
