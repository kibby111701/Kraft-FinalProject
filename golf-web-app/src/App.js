import './App.css';
import React, {useEffect, useState} from "react";
import ReactPlayer from 'react-player'

class Video extends React.Component {

  constructor(props) {
    super(props);
  }

  render () {
      return (
      <div className='player-wrapper'>
          <ReactPlayer
          className='react-player fixed-bottom'
          url={this.props.videoPath}
          width='100%'
          height='100%'
          controls = {true}

          />
      </div>
      )
  }
}

// const test = async () => {
//   const result = await fetch('test.com');

//   return result.json();
// }

// class FileUpload extends React.Component {
//   constructor(props){
//     super(props);
  

//     this.state = {vidName: ''};
//     this.handleUpload = this.handleUpload.bind(this);
//   }

//   handleUpload(ev){
//     ev.preventDefault();
//     const data = new FormData();

//     data.append('file', this.uploadInput.files[0]);

//     fetch('/upload', {method: 'POST', body: data}).then(
//       (response) => {
//         response.json().then((body) => {
//           if (body.status === 'success'){
//             console.log(body.filename);
//             this.setState({vidName: body.filename})
//           }
//         });
//       });
//   }

//   render() {
//     return (
//       <form onSubmit={this.handleUpload}>
//         <div>
//           <input ref={(ref) => { this.uploadInput = ref; }} type="file" />
//         </div>
//         <br />
//         <div>
//           <button>Upload</button>
//         </div>
//         {this.state.vidName ? <Video/>: null}
//       </form>
//     )
//   }
// }

function App() {

  const [ videoPath, setVideoPath ] = useState('/static/videos/base.mov');
  const [ loading, setLoading ] = useState(false);
  const [ statistics, setStatistics ] = useState(null);
  const [ error, setError ] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault()
    try{
      const data = new FormData();
      data.append('file', e.target.files[0])
      const res = await fetch('/upload', {
        method: 'POST', 
        body: data,
      });

      const resData = await res.json();
      if (res.ok){
        setVideoPath('/static/videos/base.mp4');
        console.log('success');
      } else {
        console.error(`Failed: ${resData.status}`);
      }
    } catch (error) {
      console.error('Error: ', error);
    }

  }

  const generateStats = async (e) => {
    setLoading(true);
    setError(null);

    try{
      const response = await fetch('/generate', {mehtod: 'GET',});
      
      const resdata = await response.json();
      console.log(resdata.status);
      console.log(resdata.status == 'success');
      if (resdata.status === 'success'){
        console.log(resdata.data);
        setStatistics(resdata.data);
      }
      else {
        setError(resdata.error);
      }

    } catch (err) {
      setError('Error fetching stats');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>GolfTrace</h1>
        <input type="file" onChange={handleUpload}/>
        {videoPath && <Video videoPath={videoPath}/>}
        <br></br>
        <div>
          <button onClick={generateStats} disabled={!videoPath} className='button'>Generate Stats!</button>
          {loading && <p>Loading...</p>}
          {error && <p>{error}</p>}
          {statistics && (
            <div>
              <h2>Statistics:</h2>
              <ul>
                {Object.entries(statistics).map(([key, value]) => (
                  <li key={key}>
                    <strong>{key}:</strong> {value}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
      </header>
      
    </div>
  );
}

export default App;
