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
import { withStyles, makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TablePagination from '@material-ui/core/TablePagination';
import VisibilityIcon from '@material-ui/icons/Visibility';
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';
import IconButton from '@material-ui/core/IconButton';

import { API, graphqlOperation } from 'aws-amplify';
import { deleteGeofence, deleteGeofenceMessage } from '../graphql/mutations'
import { Link } from 'react-router-dom';
import { indigo } from '@material-ui/core/colors';

const useStyles = makeStyles({
  table: {
    maxWidth: 900,
    margin: "auto"
  },
});

const StyledTableCell = withStyles((theme) => ({
  head: {
    backgroundColor: indigo[200],
    color: theme.palette.common.black,
  },
  body: {
    fontSize: 14,
  },
}))(TableCell);

const row = (x, i, deleteGeofence, queryGeofences) => (
  <TableRow key = {`tr-${i}`} >
    <TableCell key={`trc-${1}`} style={{ width: "40%"}}>
      {x['name']}
    </TableCell>
    <TableCell key={`trc-${2}`} style={{ width: "30%"}}>
      {x['branch']}
    </TableCell>
    <TableCell key={`trc-${3}`} style={{ width: "20%"}}>
      {x['city']}
    </TableCell>
    <TableCell style={{ width: "5%"}}>
      <Link to={{
          pathname: "/geofenceDetails",
          obj: x
      }}>
        <IconButton 
          color="primary"
          variant="contained" 
          size="small"
        >
          <VisibilityIcon fontSize="small" style={{ color: '#337ab7'}}/>
        </IconButton>
      </Link>
    </TableCell>
    <TableCell style={{ width: "5%"}}>      
      <Link to={{
          pathname: "/geofenceEdit",
          obj: x,
          queryGeofences: queryGeofences
      }}>
        <IconButton 
          color="primary"
          variant="contained" 
          size="small"
        >
          <EditIcon fontSize="small" style={{ color: '#337ab7'}}/>
        </IconButton>
      </Link>
    </TableCell>
    <TableCell style={{ width: "5%"}}>
      
      <IconButton 
        color="primary"
        variant="contained" 
        size="small"
        onClick={e => deleteGeofence(e, x['id'])}     
      >
        <DeleteIcon fontSize="small" style={{ color: '#337ab7'}} />
      </IconButton>

    </TableCell>
  </TableRow>
);

export default function GeofenceTable( {header, data, queryGeofences} ) {
  const classes = useStyles();

  const [rowsPerPage, setRowsPerPage] = React.useState(5);
  const [page, setPage] = React.useState(0);

  React.useEffect(() => {
    queryGeofences();
  }, []);

  //const emptyRows = rowsPerPage - Math.min(rowsPerPage, rows.length - page * rowsPerPage);

  const handleChangePage = async (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = async (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const removeGeofence = async (e, id) => {
    e.preventDefault();
    
    try {
      let resultDeleteGeofenceMessage = await API.graphql(graphqlOperation(
        deleteGeofenceMessage, {
          template: id
        }
      ));
      console.log('Delete Geofence Message Response =>' + JSON.stringify(resultDeleteGeofenceMessage, null, 4));
    } catch (err) {
      console.error('Err Delete Geofence => ' + JSON.stringify(err, null, 4))
    }

    try {
      let resultDeletePremiumGeofenceMessage = await API.graphql(graphqlOperation(
        deleteGeofenceMessage, {
          template: `${id}-PREMIUM`
        }
      ));
      console.log('Delete Premium Geofence Message Response =>' + JSON.stringify(resultDeletePremiumGeofenceMessage, null, 4));
    } catch (err) {
      console.error('Err Delete Geofence => ' + JSON.stringify(err, null, 4))
    }
    
    try {
      let resultDeleteGeofence = await API.graphql(graphqlOperation(
        deleteGeofence, {
          input: {
            id: id
          }
        }
      ));
      console.log('Delete Geofence Response =>' + JSON.stringify(resultDeleteGeofence, null, 4));
    } catch (err) {
      console.error('Err Delete Geofence => ' + JSON.stringify(err, null, 4))
    }    

    queryGeofences();
  };
    
  return (
    <div>
      <TableContainer>
        <Table className={classes.table} aria-label="customized table">
          <TableHead>
            <TableRow>
            <StyledTableCell key = {`thc-${1}`}>Name</StyledTableCell>      
            <StyledTableCell key = {`thc-${2}`}>Branch</StyledTableCell>      
            <StyledTableCell key = {`thc-${3}`}>City</StyledTableCell>      
            <StyledTableCell key = {`thc-${4}`}>Details</StyledTableCell>  
            <StyledTableCell key = {`thc-${5}`}>Edit</StyledTableCell>  
            <StyledTableCell key = {`thc-${6}`}>Delete</StyledTableCell>  
            </TableRow>
          </TableHead>
          <TableBody>
            { data
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((x, i) => row(x, i, removeGeofence, queryGeofences)) 
            }
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        style={{ width:'1180px' }}
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={data.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onChangePage={handleChangePage}
        onChangeRowsPerPage={handleChangeRowsPerPage}
      />
      
    </div>            
  );
}
