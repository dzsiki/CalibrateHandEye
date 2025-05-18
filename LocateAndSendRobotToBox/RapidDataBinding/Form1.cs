using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using ABB.Robotics;
using ABB.Robotics.Controllers;
using ABB.Robotics.Controllers.RapidDomain;
using ABB.Robotics.Controllers.MotionDomain;
using ABB.Robotics.Controllers.ConfigurationDomain;
using ABB.Robotics.Controllers.Discovery;



namespace RapidDataBinding
{
    public partial class Form1 : Form
    {
        ABB.Robotics.Controllers.Controller objController;
        private NetworkScanner objNetworkWatcher = null;
        RapidData data1;
        RapidData data2;
        RapidData data3;
        RapidData data4;
        ABB.Robotics.Controllers.RapidDomain.Num _num1;
        ABB.Robotics.Controllers.RapidDomain.Num _num2;
        ABB.Robotics.Controllers.RapidDomain.Num _num3;
        ABB.Robotics.Controllers.RapidDomain.Num _num4;
        double num1;
        double num2;
        double num3;
        double num4;

        private TcpListener tcpListener;
        private Thread listenerThread;
        private Mastership ms;


        private void StartTcpServer()
        {
            int port = 5000;  // A port, amin figyelni fogunk
            tcpListener = new TcpListener(IPAddress.Any, port);
            tcpListener.Start();
            listenerThread = new Thread(new ThreadStart(ListenForClients));
            listenerThread.IsBackground = true;
            listenerThread.Start();
        }

        private void HandleClient(object obj)
        {
            TcpClient tcpClient = (TcpClient)obj;
            NetworkStream stream = tcpClient.GetStream();
            byte[] buffer = new byte[1024];
            int bytesRead;

            while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) != 0)
            {
                string data = Encoding.ASCII.GetString(buffer, 0, bytesRead);
                Console.WriteLine(data);

                string[] dataarray = data.Split(';');

                foreach (DataGridViewRow row in dataGridView1.Rows)
                {
                    if (row.Cells["VariableName"].Value != null && row.Cells["VariableName"].Value.ToString() == "xoffs")
                    {
                        row.Cells["Value"].Value = dataarray[0];
                    }
                }
                foreach (DataGridViewRow row in dataGridView1.Rows)
                {
                    if (row.Cells["VariableName"].Value != null && row.Cells["VariableName"].Value.ToString() == "yoffs")
                    {
                        row.Cells["Value"].Value = dataarray[1];
                    }
                }
                foreach (DataGridViewRow row in dataGridView1.Rows)
                {
                    if (row.Cells["VariableName"].Value != null && row.Cells["VariableName"].Value.ToString() == "zoffs")
                    {
                        row.Cells["Value"].Value = dataarray[2];
                    }
                }

                try
                {
                    objController.Rapid.GetTask("T_ROB1").GetModule("Module1").GetRapidData("xoffs").StringValue = dataarray[0];
                    objController.Rapid.GetTask("T_ROB1").GetModule("Module1").GetRapidData("yoffs").StringValue = dataarray[1];
                    objController.Rapid.GetTask("T_ROB1").GetModule("Module1").GetRapidData("zoffs").StringValue = dataarray[2];
                    objController.Rapid.Start();
                }
                catch (Exception err)
                {
                    Console.WriteLine(err);
                }
            }

            tcpClient.Close();
        }

        // A kliensek figyelése
        private void ListenForClients()
        {
            while (true)
            {
                try
                {
                    // Várunk egy új kapcsolatot
                    TcpClient tcpClient = tcpListener.AcceptTcpClient();
                    Thread clientThread = new Thread(new ParameterizedThreadStart(HandleClient));
                    clientThread.IsBackground = true;
                    clientThread.Start(tcpClient);
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Hiba történt: " + ex.Message);
                }
            }
        }


        public Form1()
        {
            InitializeComponent();
            createcontroler();
            listmethod();

            StartTcpServer();
            this.FormClosing += new FormClosingEventHandler(this.Form1_Closing);
        }

        public void Form1_Closing(object sender, EventArgs e)
        {
            ms.Release();
        }

        public void createcontroler()
        {
            this.objNetworkWatcher = new NetworkScanner();
            objNetworkWatcher.GetControllers(NetworkScannerSearchCriterias.Real);

            ControllerInfoCollection objControllerInfoCollection = objNetworkWatcher.Controllers;
            foreach (ControllerInfo cont in objControllerInfoCollection)
            {
                Console.WriteLine(cont);
                Console.WriteLine(cont.IsVirtual);
            }
            objController = new Controller(objControllerInfoCollection[0]);

            UserInfo admin = new UserInfo("schaffer", "robotika");
            objController.Logon(admin);

            ms = Mastership.Request(objController.Rapid);
        }
        public void listmethod()
        {
            data1 = objController.Rapid.GetTask("T_ROB1").GetModule("Module1").GetRapidData("xoffs");
            data1.ValueChanged += new EventHandler<DataValueChangedEventArgs>(data1_ValueChanged);
            data2 = objController.Rapid.GetTask("T_ROB1").GetModule("Module1").GetRapidData("yoffs");
            data2.ValueChanged +=new EventHandler<DataValueChangedEventArgs>(data2_ValueChanged);
            data3 = objController.Rapid.GetTask("T_ROB1").GetModule("Module1").GetRapidData("zoffs");
            data3.ValueChanged +=new EventHandler<DataValueChangedEventArgs>(data3_ValueChanged);
            data4 = objController.Rapid.GetTask("T_ROB1").GetModule("Module1").GetRapidData("xoffs");
            data4.ValueChanged +=new EventHandler<DataValueChangedEventArgs>(data4_ValueChanged);

            _num1 = (ABB.Robotics.Controllers.RapidDomain.Num)data1.Value;
            num1 = _num1.Value;
            _num2 = (ABB.Robotics.Controllers.RapidDomain.Num)data2.Value;
            num2 = _num2.Value;
            _num3 = (ABB.Robotics.Controllers.RapidDomain.Num)data3.Value;
            num3 = _num3.Value;
            _num4 = (ABB.Robotics.Controllers.RapidDomain.Num)data4.Value;
            num4 = _num4.Value;
            dataGridView1.Rows.Add(data1.Symbol.Scope[0], data1.Symbol.Scope[1], data1.Symbol.Scope[2], num1);
            dataGridView1.Rows.Add(data2.Symbol.Scope[0], data2.Symbol.Scope[1], data2.Symbol.Scope[2], num2);
            dataGridView1.Rows.Add(data3.Symbol.Scope[0], data3.Symbol.Scope[1], data3.Symbol.Scope[2], num3);
            dataGridView1.Rows.Add(data4.Symbol.Scope[0], data4.Symbol.Scope[1], data4.Symbol.Scope[2], num4);
            dataGridView1.AutoGenerateColumns = false;

        }

        void OnRowHeaderMouseClick(object sender, DataGridViewCellMouseEventArgs e)
        {
            if (dataGridView1.SelectedRows.Count > 0)
            {


                this.textBox4.Text = dataGridView1.SelectedRows[0].Cells[0].Value.ToString();
                this.textBox3.Text = dataGridView1.SelectedRows[0].Cells[1].Value.ToString();
                this.textBox2.Text = dataGridView1.SelectedRows[0].Cells[2].Value.ToString();
                this.textBox1.Text = dataGridView1.SelectedRows[0].Cells[3].Value.ToString();

            }

        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            
            try { 
                objController.Rapid.GetTask(textBox4.Text).GetModule(textBox3.Text).GetRapidData(textBox2.Text).StringValue = textBox1.Text;
                

                foreach (DataGridViewRow row in dataGridView1.Rows)
                {
                    if(row.Cells["VariableName"].Value != null && row.Cells["VariableName"].Value.ToString() == textBox2.Text)
                    {
                        row.Cells["Value"].Value = textBox1.Text;
                    }
                }

            } catch (Exception err)
            {
                Console.WriteLine(err);
            }
            
        }

        private void data1_ValueChanged(object sender, DataValueChangedEventArgs e)
        {

            string str = sender.ToString();
            Console.WriteLine(str);
            objController.Rapid.Start();

        }

        private void data2_ValueChanged(object sender, DataValueChangedEventArgs e)
        {

            string str = sender.ToString();


        }
        private void data3_ValueChanged(object sender, DataValueChangedEventArgs e)
        {

            string str = sender.ToString();


        }
        private void data4_ValueChanged(object sender, DataValueChangedEventArgs e)
        {

            string str = sender.ToString();


        }

        private void button1_Click(object sender, EventArgs e)
        {
            objController.Rapid.GetTask("T_ROB1").ResetProgramPointer();
            objController.Rapid.GetTask("T_ROB1").SetProgramPointer("Module1", "Main");

            foreach (DataGridViewRow row in dataGridView1.Rows)
            {
                if (row.Cells["VariableName"].Value != null && row.Cells["VariableName"].Value.ToString() == "xoffs")
                { objController.Rapid.GetTask("T_ROB1").GetModule("Module1").GetRapidData("xoffs").StringValue = row.Cells["Value"].Value.ToString(); }
            }

            foreach (DataGridViewRow row in dataGridView1.Rows)
            {
                if (row.Cells["VariableName"].Value != null && row.Cells["VariableName"].Value.ToString() == "yoffs")
                { objController.Rapid.GetTask("T_ROB1").GetModule("Module1").GetRapidData("yoffs").StringValue = row.Cells["Value"].Value.ToString(); }
            }

            foreach (DataGridViewRow row in dataGridView1.Rows)
            {if (row.Cells["VariableName"].Value != null && row.Cells["VariableName"].Value.ToString() == "zoffs")
                {objController.Rapid.GetTask("T_ROB1").GetModule("Module1").GetRapidData("zoffs").StringValue = row.Cells["Value"].Value.ToString();}}


            

            objController.Rapid.GetTask("T_ROB1").Start();
            objController.Rapid.Start();
        }
    }
}

