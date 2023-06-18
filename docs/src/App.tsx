import { API } from '@stoplight/elements';
import '@stoplight/elements/styles.min.css';


function App() {
  return (
    <div className="App">
      <API
        apiDescriptionUrl={import.meta.env.VITE_API_SCHEMA_URL}
      />
    </div>
  );
}

export default App;
